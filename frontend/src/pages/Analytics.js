import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { mockCourses, mockUsers, mockEnrollments } from '../data/mockData';
import { 
  BarChart, 
  TrendingUp, 
  Users, 
  BookOpen, 
  Award,
  Calendar,
  Target,
  Activity
} from 'lucide-react';

const Analytics = () => {
  // Calculate analytics data
  const totalUsers = mockUsers.length;
  const totalCourses = mockCourses.length;
  const totalEnrollments = mockEnrollments.length;
  const avgProgress = mockEnrollments.reduce((sum, e) => sum + e.progress, 0) / mockEnrollments.length || 0;
  
  const coursePopularity = mockCourses.map(course => ({
    ...course,
    enrollmentCount: mockEnrollments.filter(e => e.courseId === course.id).length
  })).sort((a, b) => b.enrollmentCount - a.enrollmentCount);

  const roleDistribution = [
    { role: 'Students', count: mockUsers.filter(u => u.role === 'learner').length, color: 'bg-blue-500' },
    { role: 'Instructors', count: mockUsers.filter(u => u.role === 'instructor').length, color: 'bg-green-500' },
    { role: 'Admins', count: mockUsers.filter(u => u.role === 'admin').length, color: 'bg-red-500' }
  ];

  const completionStats = [
    { status: 'Completed', count: mockEnrollments.filter(e => e.progress === 100).length, color: 'bg-green-500' },
    { status: 'In Progress', count: mockEnrollments.filter(e => e.progress > 0 && e.progress < 100).length, color: 'bg-orange-500' },
    { status: 'Not Started', count: mockEnrollments.filter(e => e.progress === 0).length, color: 'bg-gray-500' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive insights into your LearningFwiend platform</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Users</p>
                <p className="text-2xl font-bold text-blue-700">{totalUsers}</p>
                <p className="text-xs text-blue-600 mt-1">+12% from last month</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Total Courses</p>
                <p className="text-2xl font-bold text-green-700">{totalCourses}</p>
                <p className="text-xs text-green-600 mt-1">+8% from last month</p>
              </div>
              <BookOpen className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Enrollments</p>
                <p className="text-2xl font-bold text-orange-700">{totalEnrollments}</p>
                <p className="text-xs text-orange-600 mt-1">+25% from last month</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Avg Progress</p>
                <p className="text-2xl font-bold text-purple-700">{Math.round(avgProgress)}%</p>
                <p className="text-xs text-purple-600 mt-1">+5% from last month</p>
              </div>
              <Target className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Course Popularity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart className="w-5 h-5 mr-2" />
              Most Popular Courses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {coursePopularity.slice(0, 5).map((course) => (
                <div key={course.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1">
                    <img 
                      src={course.thumbnail} 
                      alt={course.title}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{course.title}</p>
                      <p className="text-sm text-gray-600">by {course.instructor}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{course.enrollmentCount}</p>
                    <p className="text-xs text-gray-500">enrollments</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* User Role Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="w-5 h-5 mr-2" />
              User Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {roleDistribution.map((item) => (
                <div key={item.role} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{item.role}</span>
                    <span className="text-sm font-semibold">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${item.color}`}
                      style={{ width: `${(item.count / totalUsers) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Completion Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              Course Completion Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {completionStats.map((stat) => (
                <div key={stat.status} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full ${stat.color}`}></div>
                    <span className="font-medium text-gray-900">{stat.status}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xl font-bold text-gray-900">{stat.count}</span>
                    <p className="text-xs text-gray-500">
                      {Math.round((stat.count / totalEnrollments) * 100)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">New user registration</p>
                  <p className="text-xs text-gray-600">Mike Johnson joined as a student</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Course completed</p>
                  <p className="text-xs text-gray-600">Sarah finished React Development Fundamentals</p>
                  <p className="text-xs text-gray-500">5 hours ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">New course published</p>
                  <p className="text-xs text-gray-600">Digital Marketing Mastery is now available</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Course Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Course Performance Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Course</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Enrollments</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Avg Progress</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody>
                {mockCourses.map((course) => {
                  const enrollments = mockEnrollments.filter(e => e.courseId === course.id);
                  const avgProgress = enrollments.length > 0 
                    ? enrollments.reduce((sum, e) => sum + e.progress, 0) / enrollments.length 
                    : 0;
                  
                  return (
                    <tr key={course.id} className="border-b border-gray-100">
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <img 
                            src={course.thumbnail} 
                            alt={course.title}
                            className="w-10 h-10 rounded-lg object-cover"
                          />
                          <div>
                            <p className="font-medium text-gray-900">{course.title}</p>
                            <p className="text-sm text-gray-600">{course.category}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-semibold">{enrollments.length}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <Progress value={avgProgress} className="w-20 h-2" />
                          <span className="text-sm font-medium">{Math.round(avgProgress)}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
                          {course.status}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;