import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { 
  Home, 
  BookOpen, 
  User, 
  Settings, 
  Users, 
  BarChart, 
  PlusCircle,
  Award,
  MessageSquare,
  LogOut,
  ClipboardCheck,
  Shield,
  Building2
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout, isAdmin, isInstructor, isLearner } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { 
      path: '/dashboard', 
      icon: Home, 
      label: 'Dashboard', 
      roles: ['admin', 'instructor', 'learner'] 
    },
    { 
      path: '/courses', 
      icon: BookOpen, 
      label: 'Courses', 
      roles: ['admin', 'instructor', 'learner'] 
    },
    { 
      path: '/programs', 
      icon: Award, 
      label: 'Programs', 
      roles: ['admin', 'instructor'] 
    },
    { 
      path: '/classrooms', 
      icon: Users, 
      label: 'Classrooms', 
      roles: ['admin', 'instructor', 'learner'] 
    },
    { 
      path: '/create-course', 
      icon: PlusCircle, 
      label: 'Create Course', 
      roles: ['admin', 'instructor'] 
    },
    { 
      path: '/quiz-results', 
      icon: ClipboardCheck, 
      label: 'Quiz Results', 
      roles: ['admin', 'instructor'] 
    },
    { 
      path: '/users', 
      icon: Users, 
      label: 'Users', 
      roles: ['admin'] 
    },
    { 
      path: '/departments', 
      icon: Building2, 
      label: 'Departments', 
      roles: ['admin'] 
    },
    { 
      path: '/loginpal-status', 
      icon: Shield, 
      label: 'LoginPal Status', 
      roles: ['admin'] 
    },
    { 
      path: '/analytics', 
      icon: BarChart, 
      label: 'Analytics', 
      roles: ['admin', 'instructor'] 
    },
    { 
      path: '/certificates', 
      icon: Award, 
      label: 'Certificates', 
      roles: ['learner'] 
    },
    { 
      path: '/announcements', 
      icon: MessageSquare, 
      label: 'Announcements', 
      roles: ['admin', 'instructor', 'learner'] 
    },
    { 
      path: '/profile', 
      icon: User, 
      label: 'Profile', 
      roles: ['admin', 'instructor', 'learner'] 
    }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_learn-hub-60/artifacts/w6mk6gy1_ChatGPT%20Image%20Aug%205%2C%202025%2C%2001_02_09%20PM.png"
              alt="LearningFwiend Mascot"
              className="w-8 h-8 object-contain"
            />
          </div>
          <h1 className="text-xl font-bold text-gray-900">LearningFwiend</h1>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {filteredMenuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Button
              key={item.path}
              variant={isActive ? "default" : "ghost"}
              className={`w-full justify-start space-x-3 h-12 ${
                isActive 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              onClick={() => navigate(item.path)}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Button>
          );
        })}
      </nav>

      {/* User Profile Section */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 mb-4">
          <Avatar className="h-10 w-10">
            <AvatarImage src={user?.avatar} alt={user?.name} />
            <AvatarFallback>{user?.name?.charAt(0)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {user?.role}
            </p>
          </div>
        </div>
        
        <Button
          variant="outline"
          className="w-full justify-start space-x-2 text-gray-700 hover:bg-gray-50"
          onClick={handleLogout}
        >
          <LogOut className="w-4 h-4" />
          <span>Log out</span>
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;