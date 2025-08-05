import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import StudentDashboard from '../components/dashboards/StudentDashboard';
import InstructorDashboard from '../components/dashboards/InstructorDashboard';
import AdminDashboard from '../components/dashboards/AdminDashboard';

const Dashboard = () => {
  const { user } = useAuth();

  if (user?.role === 'admin') {
    return <AdminDashboard />;
  }

  if (user?.role === 'instructor') {
    return <InstructorDashboard />;
  }

  return <StudentDashboard />;
};

export default Dashboard;