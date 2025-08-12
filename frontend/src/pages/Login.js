import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { BookOpen, Eye, EyeOff } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import LoginPalButton from '../components/auth/LoginPalButton';
import PasswordChangeModal from '../components/PasswordChangeModal';

const Login = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);
  const { user, login, requiresPasswordChange, changePassword } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Redirect if already logged in and password change not required
  useEffect(() => {
    if (user && !requiresPasswordChange) {
      navigate('/dashboard');
    }
    // Don't automatically show modal here - let login success handle it
  }, [user, requiresPasswordChange, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(usernameOrEmail, password);
    
    if (result.success) {
      if (result.requires_password_change) {
        // Show password change modal and don't navigate
        setShowPasswordChangeModal(true);
        toast({
          title: "Welcome!",
          description: "Please change your temporary password to continue.",
        });
      } else {
        toast({
          title: "Welcome back!",
          description: `Logged in as ${result.user.full_name}`,
        });
        navigate('/dashboard');
      }
    } else {
      toast({
        title: "Login failed",
        description: result.error,
        variant: "destructive",
      });
    }
    
    setLoading(false);
  };

  const handlePasswordChangeSuccess = () => {
    setShowPasswordChangeModal(false);
    toast({
      title: "Password updated!",
      description: "Your password has been successfully changed.",
    });
    navigate('/dashboard');
  };

  const quickLogin = (role) => {
    const credentials = {
      admin: { username: 'admin', password: 'NewAdmin123!' },
      instructor: { username: 'instructor', password: 'Instructor123!' },
      learner: { username: 'student', password: 'Student123!' }
    };
    
    setUsernameOrEmail(credentials[role].username);
    setPassword(credentials[role].password);
  };

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">LearningFwiend</h1>
            </div>
            <p className="text-gray-600">Sign in to your account</p>
          </div>

          <Card className="shadow-xl border-0">
            <CardHeader>
              <CardTitle className="text-center text-xl">Welcome Back</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="usernameOrEmail">Username or Email</Label>
                  <Input
                    id="usernameOrEmail"
                    type="text"
                    placeholder="Enter your username or email"
                    value={usernameOrEmail}
                    onChange={(e) => setUsernameOrEmail(e.target.value)}
                    required
                    className="h-12"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-12 pr-12"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-2 top-2 h-8 w-8 p-0"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full h-12 bg-blue-600 hover:bg-blue-700"
                  disabled={loading}
                >
                  {loading ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>

              {/* OAuth Separator */}
              <div className="my-6 flex items-center">
                <div className="flex-1 border-t border-gray-300"></div>
                <div className="mx-4 text-sm text-gray-500">or</div>
                <div className="flex-1 border-t border-gray-300"></div>
              </div>

              {/* LoginPal OAuth Button */}
              <LoginPalButton />

              {/* Quick Login Demo Buttons */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-500 text-center mb-3">Quick Demo Login:</p>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => quickLogin('admin')}
                    type="button"
                  >
                    <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                    Login as Admin
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => quickLogin('instructor')}
                    type="button"
                  >
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                    Login as Instructor
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => quickLogin('learner')}
                    type="button"
                  >
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                    Login as Student
                  </Button>
                </div>
                <div className="mt-3 p-2 bg-blue-50 rounded-lg">
                  <p className="text-xs text-blue-700 text-center">
                    <strong>Note:</strong> All demo accounts use temporary passwords and will require password change on first login.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Password Change Modal */}
      <PasswordChangeModal
        isOpen={showPasswordChangeModal}
        onClose={() => setShowPasswordChangeModal(false)}
        onSuccess={handlePasswordChangeSuccess}
        currentUser={user}
      />
    </>
  );
};

export default Login;