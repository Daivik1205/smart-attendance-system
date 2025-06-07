// components/Attendance.js
import React, { useState, useEffect } from 'react';
import { database } from '../firebase'; 
import { ref, onValue } from 'firebase/database';
import { Table, Card, DatePicker, Tag, Typography, Space, Spin } from 'antd';
import dayjs from 'dayjs';
import isBetween from 'dayjs/plugin/isBetween';
import { CalendarOutlined } from '@ant-design/icons';

dayjs.extend(isBetween);

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

function Attendance() {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dates, setDates] = useState([dayjs().subtract(7, 'day'), dayjs()]);

  useEffect(() => {
    setLoading(true);
    const attendanceRef = ref(database, 'attendance');
    const unsubscribe = onValue(attendanceRef, (snapshot) => {
      const data = snapshot.val();
      if (!data) {
        setAttendance([]);
        setLoading(false);
        return;
      }
      
      const allRecords = [];
      Object.keys(data).forEach((date) => {
        const dateData = data[date];
        Object.keys(dateData).forEach((studentId) => {
          const studentData = dateData[studentId];
          const recordTimestamp = studentData.timestamp || '';
          const recordDate = dayjs(date);

          if (recordDate.isBetween(dates[0], dates[1], null, '[]')) {
            allRecords.push({
              key: `${date}-${studentId}`,
              date: dayjs(date).format('DD MMM YYYY'),
              studentId,
              name: studentData.name || 'N/A',
              status: studentData.status === 'present' ? 'Present' : 'Absent',
              time: recordTimestamp ? dayjs(recordTimestamp).format('HH:mm:ss') : 'N/A',
            });
          }
        });
      });

      setAttendance(allRecords);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [dates]);

  const columns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => dayjs(a.date).unix() - dayjs(b.date).unix(),
    },
    {
      title: 'Student ID',
      dataIndex: 'studentId',
      key: 'studentId',
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      filters: [
        { text: 'Present', value: 'Present' },
        { text: 'Absent', value: 'Absent' },
      ],
      onFilter: (value, record) => record.status === value,
      render: (text) => (
        <Tag color={text === 'Present' ? 'green' : 'red'}>
          {text}
        </Tag>
      ),
    },
  ];

  return (
    <div style={{ padding: '1rem' }}>
      <Card
        title={
          <Space>
            <CalendarOutlined />
            <Text strong>Attendance Records</Text>
          </Space>
        }
        extra={
          <RangePicker
            value={dates}
            onChange={setDates}
            disabledDate={current => current && current > dayjs().endOf('day')}
            style={{ width: 250 }}
            allowClear={false}
          />
        }
        bordered={false}
        style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.09)' }}
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={attendance}
            rowKey="key"
            pagination={{ 
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} records`,
            }}
            locale={{
              emptyText: 'No attendance records found for the selected period'
            }}
          />
        </Spin>
      </Card>
    </div>
  );
}

export default Attendance;