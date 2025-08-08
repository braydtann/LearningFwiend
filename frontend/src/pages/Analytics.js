import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockCourses, mockUsers, mockEnrollments, mockQuizAttempts, mockClassrooms, mockClassroomEnrollments, mockDepartments } from '../data/mockData';
import { 
  BarChart, 
  TrendingUp, 
  Users, 
  BookOpen, 
  Award,
  Calendar,
  Target,
  Activity,
  Clock,
  Filter,
  Download,
  LineChart,
  PieChart,
  User,
  GraduationCap,
  Building
} from 'lucide-react';

const Analytics = () => {
  // State for filters and date selection
  const [dateRange, setDateRange] = useState({
    startDate: '2024-01-01',
    endDate: '2024-12-31'
  });
  const [selectedInstructor, setSelectedInstructor] = useState('all');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [selectedCourse, setSelectedCourse] = useState('all');
  const [selectedClassroom, setSelectedClassroom] = useState('all');
  const [performanceTrendFilter, setPerformanceTrendFilter] = useState('all'); // New filter for trends
  const [activeView, setActiveView] = useState('overview');

  // Get unique instructors, departments, and classrooms
  const instructors = useMemo(() => {
    const instructorList = [...new Set(mockCourses.map(course => course.instructor))];
    return instructorList;
  }, []);

  const departments = useMemo(() => {
    const deptList = [...new Set(mockCourses.map(course => course.category))];
    return deptList;
  }, []);

  const classrooms = useMemo(() => {
    return mockClassrooms.map(classroom => ({
      id: classroom.id,
      name: classroom.name,
      batchId: classroom.batchId
    }));
  }, []);

  // Filter data based on selections and date range
  const filteredData = useMemo(() => {
    const filterDate = (date) => {
      return date >= dateRange.startDate && date <= dateRange.endDate;
    };

    let filteredCourses = mockCourses;
    if (selectedInstructor !== 'all') {
      filteredCourses = filteredCourses.filter(course => course.instructor === selectedInstructor);
    }
    if (selectedDepartment !== 'all') {
      filteredCourses = filteredCourses.filter(course => course.category === selectedDepartment);
    }
    if (selectedCourse !== 'all') {
      filteredCourses = filteredCourses.filter(course => course.id === selectedCourse);
    }

    const courseIds = filteredCourses.map(course => course.id);
    let filteredEnrollments = mockEnrollments.filter(enrollment => 
      courseIds.includes(enrollment.courseId) && 
      filterDate(enrollment.enrolledAt)
    );

    // Filter by classroom if selected
    if (selectedClassroom !== 'all') {
      const classroomStudents = mockClassroomEnrollments
        .filter(ce => ce.classroomId === selectedClassroom)
        .map(ce => ce.studentId);
      filteredEnrollments = filteredEnrollments.filter(enrollment => 
        classroomStudents.includes(enrollment.userId)
      );
    }

    let filteredQuizAttempts = mockQuizAttempts.filter(attempt => 
      courseIds.includes(attempt.courseId) && 
      filterDate(attempt.completedAt)
    );

    // Filter quiz attempts by classroom if selected
    if (selectedClassroom !== 'all') {
      const classroomStudents = mockClassroomEnrollments
        .filter(ce => ce.classroomId === selectedClassroom)
        .map(ce => ce.studentId);
      filteredQuizAttempts = filteredQuizAttempts.filter(attempt => 
        classroomStudents.includes(attempt.userId)
      );
    }

    return {
      courses: filteredCourses,
      enrollments: filteredEnrollments,
      quizAttempts: filteredQuizAttempts
    };
  }, [dateRange, selectedInstructor, selectedDepartment, selectedCourse, selectedClassroom]);

  // Calculate key metrics
  const metrics = useMemo(() => {
    const { courses, enrollments, quizAttempts } = filteredData;
    
    const totalEnrollments = enrollments.length;
    const completedCourses = enrollments.filter(e => e.progress === 100).length;
    const completionRate = totalEnrollments > 0 ? (completedCourses / totalEnrollments) * 100 : 0;
    
    const totalTimeSpent = enrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0);
    const avgTimeSpent = totalEnrollments > 0 ? totalTimeSpent / totalEnrollments : 0;
    
    const quizScores = quizAttempts.map(attempt => attempt.score);
    const avgQuizScore = quizScores.length > 0 ? quizScores.reduce((sum, score) => sum + score, 0) / quizScores.length : 0;
    
    const testScores = quizAttempts.filter(attempt => attempt.isTest).map(attempt => attempt.score);
    const avgTestScore = testScores.length > 0 ? testScores.reduce((sum, score) => sum + score, 0) / testScores.length : 0;

    return {
      totalEnrollments,
      completionRate,
      avgTimeSpent,
      avgQuizScore,
      avgTestScore,
      totalQuizAttempts: quizAttempts.length,
      totalTestAttempts: testScores.length
    };
  }, [filteredData]);

  // Generate time-series data for trends based on actual filtered data
  const generateTrendData = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const { enrollments, quizAttempts } = filteredData;
    
    return months.map((month, index) => {
      const monthNumber = String(index + 1).padStart(2, '0');
      const monthData = {
        month,
        enrollments: 0,
        completions: 0,
        avgScore: 0,
        timeSpent: 0
      };

      // Filter data by month
      const monthEnrollments = enrollments.filter(e => 
        e.enrolledAt.startsWith(`2024-${monthNumber}`)
      );
      
      const monthQuizAttempts = quizAttempts.filter(a => 
        a.completedAt && a.completedAt.startsWith(`2024-${monthNumber}`)
      );

      monthData.enrollments = monthEnrollments.length;
      monthData.completions = monthEnrollments.filter(e => e.progress === 100).length;
      
      if (monthQuizAttempts.length > 0) {
        monthData.avgScore = monthQuizAttempts.reduce((sum, a) => sum + a.score, 0) / monthQuizAttempts.length;
      } else {
        monthData.avgScore = 0;
      }
      
      if (monthEnrollments.length > 0) {
        monthData.timeSpent = monthEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0) / monthEnrollments.length;
      } else {
        monthData.timeSpent = 0;
      }

      return monthData;
    });
  };

  const trendData = generateTrendData();

  // Individual performance data
  const getIndividualPerformance = () => {
    return mockUsers.filter(user => user.role === 'learner').map(user => {
      const userEnrollments = filteredData.enrollments.filter(e => e.userId === user.id);
      const userQuizzes = filteredData.quizAttempts.filter(q => q.userId === user.id);
      
      return {
        id: user.id,
        name: user.name,
        email: user.email,
        enrollments: userEnrollments.length,
        completionRate: userEnrollments.length > 0 ? 
          (userEnrollments.filter(e => e.progress === 100).length / userEnrollments.length) * 100 : 0,
        avgProgress: userEnrollments.length > 0 ?
          userEnrollments.reduce((sum, e) => sum + e.progress, 0) / userEnrollments.length : 0,
        timeSpent: userEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0),
        quizAvg: userQuizzes.length > 0 ?
          userQuizzes.reduce((sum, q) => sum + q.score, 0) / userQuizzes.length : 0,
        testAvg: userQuizzes.filter(q => q.isTest).length > 0 ?
          userQuizzes.filter(q => q.isTest).reduce((sum, q) => sum + q.score, 0) / userQuizzes.filter(q => q.isTest).length : 0
      };
    });
  };

  const individualPerformance = getIndividualPerformance();

  // Class performance data
  const getClassPerformance = () => {
    return filteredData.courses.map(course => {
      const courseEnrollments = filteredData.enrollments.filter(e => e.courseId === course.id);
      const courseQuizzes = filteredData.quizAttempts.filter(q => q.courseId === course.id);
      
      return {
        ...course,
        enrollmentCount: courseEnrollments.length,
        completionRate: courseEnrollments.length > 0 ? 
          (courseEnrollments.filter(e => e.progress === 100).length / courseEnrollments.length) * 100 : 0,
        avgProgress: courseEnrollments.length > 0 ?
          courseEnrollments.reduce((sum, e) => sum + e.progress, 0) / courseEnrollments.length : 0,
        totalTimeSpent: courseEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0),
        avgTimePerStudent: courseEnrollments.length > 0 ?
          courseEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0) / courseEnrollments.length : 0,
        quizAvg: courseQuizzes.length > 0 ?
          courseQuizzes.reduce((sum, q) => sum + q.score, 0) / courseQuizzes.length : 0,
        testAvg: courseQuizzes.filter(q => q.isTest).length > 0 ?
          courseQuizzes.filter(q => q.isTest).reduce((sum, q) => sum + q.score, 0) / courseQuizzes.filter(q => q.isTest).length : 0
      };
    });
  };

  const classPerformance = getClassPerformance();

  // Department aggregation
  const getDepartmentPerformance = () => {
    const deptStats = {};
    
    departments.forEach(dept => {
      const deptCourses = filteredData.courses.filter(course => course.category === dept);
      const deptCourseIds = deptCourses.map(course => course.id);
      const deptEnrollments = filteredData.enrollments.filter(e => deptCourseIds.includes(e.courseId));
      const deptQuizzes = filteredData.quizAttempts.filter(q => deptCourseIds.includes(q.courseId));
      
      deptStats[dept] = {
        department: dept,
        courseCount: deptCourses.length,
        enrollmentCount: deptEnrollments.length,
        completionRate: deptEnrollments.length > 0 ? 
          (deptEnrollments.filter(e => e.progress === 100).length / deptEnrollments.length) * 100 : 0,
        avgProgress: deptEnrollments.length > 0 ?
          deptEnrollments.reduce((sum, e) => sum + e.progress, 0) / deptEnrollments.length : 0,
        totalTimeSpent: deptEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0),
        avgTimePerStudent: deptEnrollments.length > 0 ?
          deptEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0) / deptEnrollments.length : 0,
        quizAvg: deptQuizzes.length > 0 ?
          deptQuizzes.reduce((sum, q) => sum + q.score, 0) / deptQuizzes.length : 0,
        testAvg: deptQuizzes.filter(q => q.isTest).length > 0 ?
          deptQuizzes.filter(q => q.isTest).reduce((sum, q) => sum + q.score, 0) / deptQuizzes.filter(q => q.isTest).length : 0
      };
    });
    
    return Object.values(deptStats);
  };

  const departmentPerformance = getDepartmentPerformance();

  // Instructor performance
  const getInstructorPerformance = () => {
    const instructorStats = {};
    
    instructors.forEach(instructor => {
      const instructorCourses = filteredData.courses.filter(course => course.instructor === instructor);
      const instructorCourseIds = instructorCourses.map(course => course.id);
      const instructorEnrollments = filteredData.enrollments.filter(e => instructorCourseIds.includes(e.courseId));
      const instructorQuizzes = filteredData.quizAttempts.filter(q => instructorCourseIds.includes(q.courseId));
      
      instructorStats[instructor] = {
        instructor,
        courseCount: instructorCourses.length,
        enrollmentCount: instructorEnrollments.length,
        completionRate: instructorEnrollments.length > 0 ? 
          (instructorEnrollments.filter(e => e.progress === 100).length / instructorEnrollments.length) * 100 : 0,
        avgProgress: instructorEnrollments.length > 0 ?
          instructorEnrollments.reduce((sum, e) => sum + e.progress, 0) / instructorEnrollments.length : 0,
        totalTimeSpent: instructorEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0),
        avgTimePerStudent: instructorEnrollments.length > 0 ?
          instructorEnrollments.reduce((sum, e) => sum + (e.timeSpent || 0), 0) / instructorEnrollments.length : 0,
        quizAvg: instructorQuizzes.length > 0 ?
          instructorQuizzes.reduce((sum, q) => sum + q.score, 0) / instructorQuizzes.length : 0,
        testAvg: instructorQuizzes.filter(q => q.isTest).length > 0 ?
          instructorQuizzes.filter(q => q.isTest).reduce((sum, q) => sum + q.score, 0) / instructorQuizzes.filter(q => q.isTest).length : 0
      };
    });
    
    return Object.values(instructorStats);
  };

  const instructorPerformance = getInstructorPerformance();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Advanced Analytics Dashboard</h1>
          <p className="text-gray-600">Comprehensive training metrics with date-based reporting and multi-level aggregation</p>
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>Export Report</span>
        </Button>
      </div>

      {/* Filters */}
      <Card className="bg-gray-50">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={dateRange.startDate}
                onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={dateRange.endDate}
                onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Department</Label>
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map(dept => (
                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Instructor</Label>
              <Select value={selectedInstructor} onValueChange={setSelectedInstructor}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Instructors</SelectItem>
                  {instructors.map(instructor => (
                    <SelectItem key={instructor} value={instructor}>{instructor}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Classroom</Label>
              <Select value={selectedClassroom} onValueChange={setSelectedClassroom}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Classrooms</SelectItem>
                  {classrooms.map(classroom => (
                    <SelectItem key={classroom.id} value={classroom.id}>
                      {classroom.name} ({classroom.batchId})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Course</Label>
              <Select value={selectedCourse} onValueChange={setSelectedCourse}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Courses</SelectItem>
                  {filteredData.courses.map(course => (
                    <SelectItem key={course.id} value={course.id}>{course.title}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Completion Rate</p>
                <p className="text-2xl font-bold text-blue-700">{metrics.completionRate.toFixed(1)}%</p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Avg Time Spent</p>
                <p className="text-2xl font-bold text-green-700">{metrics.avgTimeSpent.toFixed(1)}h</p>
              </div>
              <Clock className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Avg Quiz Score</p>
                <p className="text-2xl font-bold text-orange-700">{metrics.avgQuizScore.toFixed(1)}%</p>
              </div>
              <BarChart className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Avg Test Score</p>
                <p className="text-2xl font-bold text-purple-700">{metrics.avgTestScore.toFixed(1)}%</p>
              </div>
              <Award className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Total Enrollments</p>
                <p className="text-2xl font-bold text-gray-700">{metrics.totalEnrollments}</p>
              </div>
              <Users className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trends Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <LineChart className="w-5 h-5" />
            <span>Performance Trends Over Time</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Enrollments</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Completions</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span>Avg Score</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span>Time Spent (hrs)</span>
              </div>
            </div>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart visualization would be rendered here</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Multi-Level Analytics Tabs */}
      <Tabs value={activeView} onValueChange={setActiveView}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="individual" className="flex items-center space-x-2">
            <User className="w-4 h-4" />
            <span>Individual</span>
          </TabsTrigger>
          <TabsTrigger value="class" className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4" />
            <span>Classes</span>
          </TabsTrigger>
          <TabsTrigger value="instructor" className="flex items-center space-x-2">
            <GraduationCap className="w-4 h-4" />
            <span>Instructors</span>
          </TabsTrigger>
          <TabsTrigger value="department" className="flex items-center space-x-2">
            <Building className="w-4 h-4" />
            <span>Departments</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Individual Student Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">Student</th>
                      <th className="text-left p-3">Enrollments</th>
                      <th className="text-left p-3">Completion Rate</th>
                      <th className="text-left p-3">Avg Progress</th>
                      <th className="text-left p-3">Time Spent</th>
                      <th className="text-left p-3">Quiz Avg</th>
                      <th className="text-left p-3">Test Avg</th>
                    </tr>
                  </thead>
                  <tbody>
                    {individualPerformance.slice(0, 10).map((student) => (
                      <tr key={student.id} className="border-b">
                        <td className="p-3">
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-xs text-gray-500">{student.email}</p>
                          </div>
                        </td>
                        <td className="p-3">{student.enrollments}</td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <Progress value={student.completionRate} className="w-16 h-2" />
                            <span>{student.completionRate.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="p-3">{student.avgProgress.toFixed(1)}%</td>
                        <td className="p-3">{student.timeSpent.toFixed(1)}h</td>
                        <td className="p-3">
                          <Badge variant={student.quizAvg >= 80 ? 'default' : student.quizAvg >= 70 ? 'secondary' : 'destructive'}>
                            {student.quizAvg.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={student.testAvg >= 80 ? 'default' : student.testAvg >= 70 ? 'secondary' : 'destructive'}>
                            {student.testAvg.toFixed(1)}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="class" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Individual Class Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">Course</th>
                      <th className="text-left p-3">Instructor</th>
                      <th className="text-left p-3">Enrollments</th>
                      <th className="text-left p-3">Completion Rate</th>
                      <th className="text-left p-3">Avg Progress</th>
                      <th className="text-left p-3">Total Time</th>
                      <th className="text-left p-3">Quiz Avg</th>
                      <th className="text-left p-3">Test Avg</th>
                    </tr>
                  </thead>
                  <tbody>
                    {classPerformance.map((course) => (
                      <tr key={course.id} className="border-b">
                        <td className="p-3">
                          <div className="flex items-center space-x-3">
                            <img src={course.thumbnail} alt={course.title} className="w-10 h-10 rounded-lg object-cover" />
                            <div>
                              <p className="font-medium">{course.title}</p>
                              <p className="text-xs text-gray-500">{course.category}</p>
                            </div>
                          </div>
                        </td>
                        <td className="p-3">{course.instructor}</td>
                        <td className="p-3">{course.enrollmentCount}</td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <Progress value={course.completionRate} className="w-16 h-2" />
                            <span>{course.completionRate.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="p-3">{course.avgProgress.toFixed(1)}%</td>
                        <td className="p-3">{course.totalTimeSpent.toFixed(1)}h</td>
                        <td className="p-3">
                          <Badge variant={course.quizAvg >= 80 ? 'default' : course.quizAvg >= 70 ? 'secondary' : 'destructive'}>
                            {course.quizAvg.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={course.testAvg >= 80 ? 'default' : course.testAvg >= 70 ? 'secondary' : 'destructive'}>
                            {course.testAvg.toFixed(1)}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="instructor" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Instructor Performance Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">Instructor</th>
                      <th className="text-left p-3">Courses</th>
                      <th className="text-left p-3">Total Enrollments</th>
                      <th className="text-left p-3">Completion Rate</th>
                      <th className="text-left p-3">Avg Progress</th>
                      <th className="text-left p-3">Total Time</th>
                      <th className="text-left p-3">Quiz Avg</th>
                      <th className="text-left p-3">Test Avg</th>
                    </tr>
                  </thead>
                  <tbody>
                    {instructorPerformance.map((instructor) => (
                      <tr key={instructor.instructor} className="border-b">
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <GraduationCap className="w-4 h-4 text-blue-600" />
                            </div>
                            <span className="font-medium">{instructor.instructor}</span>
                          </div>
                        </td>
                        <td className="p-3">{instructor.courseCount}</td>
                        <td className="p-3">{instructor.enrollmentCount}</td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <Progress value={instructor.completionRate} className="w-16 h-2" />
                            <span>{instructor.completionRate.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="p-3">{instructor.avgProgress.toFixed(1)}%</td>
                        <td className="p-3">{instructor.totalTimeSpent.toFixed(1)}h</td>
                        <td className="p-3">
                          <Badge variant={instructor.quizAvg >= 80 ? 'default' : instructor.quizAvg >= 70 ? 'secondary' : 'destructive'}>
                            {instructor.quizAvg.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={instructor.testAvg >= 80 ? 'default' : instructor.testAvg >= 70 ? 'secondary' : 'destructive'}>
                            {instructor.testAvg.toFixed(1)}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="department" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Department Aggregation Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">Department</th>
                      <th className="text-left p-3">Courses</th>
                      <th className="text-left p-3">Total Enrollments</th>
                      <th className="text-left p-3">Completion Rate</th>
                      <th className="text-left p-3">Avg Progress</th>
                      <th className="text-left p-3">Total Time</th>
                      <th className="text-left p-3">Quiz Avg</th>
                      <th className="text-left p-3">Test Avg</th>
                    </tr>
                  </thead>
                  <tbody>
                    {departmentPerformance.map((dept) => (
                      <tr key={dept.department} className="border-b">
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                              <Building className="w-4 h-4 text-purple-600" />
                            </div>
                            <span className="font-medium">{dept.department}</span>
                          </div>
                        </td>
                        <td className="p-3">{dept.courseCount}</td>
                        <td className="p-3">{dept.enrollmentCount}</td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <Progress value={dept.completionRate} className="w-16 h-2" />
                            <span>{dept.completionRate.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="p-3">{dept.avgProgress.toFixed(1)}%</td>
                        <td className="p-3">{dept.totalTimeSpent.toFixed(1)}h</td>
                        <td className="p-3">
                          <Badge variant={dept.quizAvg >= 80 ? 'default' : dept.quizAvg >= 70 ? 'secondary' : 'destructive'}>
                            {dept.quizAvg.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={dept.testAvg >= 80 ? 'default' : dept.testAvg >= 70 ? 'secondary' : 'destructive'}>
                            {dept.testAvg.toFixed(1)}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;