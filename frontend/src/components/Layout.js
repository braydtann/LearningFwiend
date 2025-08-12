import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import NotificationBell from './NotificationBell';
import { Button } from './ui/button';

const Layout = ({ children }) => {
  const { user, switchRole } = useAuth();

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar with Role Switcher (for demo purposes) */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">
                {user?.role === 'admin' && 'Admin Dashboard'}
                {user?.role === 'instructor' && 'Instructor Dashboard'}
                {user?.role === 'learner' && 'Student Dashboard'}
              </h2>
              <p className="text-gray-600">Welcome back, {user?.name}</p>
            </div>
            
            {/* Role Switcher for Demo */}
            <div className="flex items-center space-x-3">
              {/* Notification Bell - only for students */}
              <NotificationBell />
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500 mr-2">Switch Role:</span>
                <Button
                  size="sm"
                  variant={user?.role === 'learner' ? 'default' : 'outline'}
                  onClick={() => switchRole('learner')}
                >
                  Student
                </Button>
                <Button
                  size="sm"
                  variant={user?.role === 'instructor' ? 'default' : 'outline'}
                  onClick={() => switchRole('instructor')}
                >
                  Instructor
                </Button>
                <Button
                  size="sm"
                  variant={user?.role === 'admin' ? 'default' : 'outline'}
                  onClick={() => switchRole('admin')}
                >
                  Admin
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Layout;