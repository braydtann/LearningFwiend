import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Toaster } from './components/ui/toaster';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import Programs from './pages/Programs';
import ProgramDetail from './pages/ProgramDetail';
import EditProgram from './pages/EditProgram';
import Classrooms from './pages/Classrooms';
import ClassroomDetail from './pages/ClassroomDetail';
import CreateCourse from './pages/CreateCourse';
import QuizTaking from './pages/QuizTaking';
import QuizResults from './pages/QuizResults';
import FinalTest from './pages/FinalTest';
import Users from './pages/Users';
import Departments from './pages/Departments';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import Certificates from './pages/Certificates';
import Categories from './pages/Categories';
import Notifications from './pages/Notifications';
import Announcements from './pages/Announcements';
import LoginPalStatus from './pages/LoginPalStatus';

// Components
import Layout from './components/Layout';

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? <Layout>{children}</Layout> : <Navigate to="/login" />;
};

const AuthRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? <Navigate to="/dashboard" /> : children;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={
              <AuthRoute>
                <Login />
              </AuthRoute>
            } />
            
            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/courses" element={
              <ProtectedRoute>
                <Courses />
              </ProtectedRoute>
            } />
            
            <Route path="/course/:id" element={
              <ProtectedRoute>
                <CourseDetail />
              </ProtectedRoute>
            } />
            
            <Route path="/create-course" element={
              <ProtectedRoute>
                <CreateCourse />
              </ProtectedRoute>
            } />
            
            <Route path="/edit-course/:id" element={
              <ProtectedRoute>
                <CreateCourse />
              </ProtectedRoute>
            } />
            
            <Route path="/quiz/:courseId/:lessonId" element={
              <ProtectedRoute>
                <QuizTaking />
              </ProtectedRoute>
            } />
            
            <Route path="/quiz-results" element={
              <ProtectedRoute>
                <QuizResults />
              </ProtectedRoute>
            } />
            
            <Route path="/final-test/:courseId" element={
              <ProtectedRoute>
                <FinalTest />
              </ProtectedRoute>
            } />
            
            <Route path="/final-test/program/:programId" element={
              <ProtectedRoute>
                <FinalTest />
              </ProtectedRoute>
            } />
            
            <Route path="/programs" element={
              <ProtectedRoute>
                <Programs />
              </ProtectedRoute>
            } />
            
            <Route path="/program/:id" element={
              <ProtectedRoute>
                <ProgramDetail />
              </ProtectedRoute>
            } />
            
            <Route path="/program/:id/edit" element={
              <ProtectedRoute>
                <EditProgram />
              </ProtectedRoute>
            } />
            
            <Route path="/classrooms" element={
              <ProtectedRoute>
                <Classrooms />
              </ProtectedRoute>
            } />
            
            <Route path="/classroom/:id" element={
              <ProtectedRoute>
                <ClassroomDetail />
              </ProtectedRoute>
            } />
            
            <Route path="/users" element={
              <ProtectedRoute>
                <Users />
              </ProtectedRoute>
            } />
            
            <Route path="/departments" element={
              <ProtectedRoute>
                <Departments />
              </ProtectedRoute>
            } />
            
            <Route path="/loginpal-status" element={
              <ProtectedRoute>
                <LoginPalStatus />
              </ProtectedRoute>
            } />
            
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } />
            
            <Route path="/certificates" element={
              <ProtectedRoute>
                <Certificates />
              </ProtectedRoute>
            } />
            
            <Route path="/categories" element={
              <Layout>
                <Categories />
              </Layout>
            } />
            
            <Route path="/notifications" element={
              <Layout>
                <Notifications />
              </Layout>
            } />
            
            <Route path="/announcements" element={
              <ProtectedRoute>
                <Announcements />
              </ProtectedRoute>
            } />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
