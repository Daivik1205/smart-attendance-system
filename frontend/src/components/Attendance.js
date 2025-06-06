import React, { useState, useEffect } from 'react';
import { db } from '../firebase';
import { ref, onValue } from 'firebase/database';
import { Table, Button, DatePicker, message } from 'antd';
import moment from 'moment';
import 'antd/dist/antd.css';

const { RangePicker } = DatePicker;

function Attendance() {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState([
    moment().startOf('day'),
    moment().endOf('day')
  ]);

  useEffect(() => {
    fetchAttendance();
  }, [dateRange]);

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      const [startDate, endDate] = dateRange;
      const dates = [];
      let current = startDate.clone();
      while (current.isSameOrBefore(endDate)) {
        dates.push(current.format('YYYY-MM-DD'));
        current.add(1, 'day');
      }
      
      const attendanceData = [];
      for (const date of dates) {
        const attendanceRef = ref(db, `attendance/${date}`);
        onValue(attendanceRef, (snapshot) => {
          const data = snapshot.val();
          if (data) {
            Object.keys(data).forEach(studentId => {
              attendanceData.push({
                key: `${date}-${studentId}`,
                date,
                name: data[studentId].name,
                time: moment(data[studentId].timestamp).format('HH:mm:ss'),
                status: data[studentId].status
              });
            });
            setAttendance([...attendanceData]);
          }
        });
      }
    } catch (error) {
      message.error('Failed to fetch attendance data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'Date', dataIndex: 'date', key: 'date' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Time', dataIndex: 'time', key: 'time' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: status => (
        <span style={{ color: status === 'present' ? 'green' : 'red' }}>
          {status.toUpperCase()}
        </span>
      )
    },
  ];

  return (
    <div className="attendance-container">
      <h1>Attendance Records</h1>
      <div className="controls">
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          disabledDate={current => current && current > moment().endOf('day')}
        />
        <Button type="primary" onClick={fetchAttendance} loading={loading}>
          Refresh
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={attendance}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}

export default Attendance;