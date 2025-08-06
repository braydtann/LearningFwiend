import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { BookOpen, Eye, EyeOff, Shield } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(email, password);
    
    if (result.success) {
      toast({
        title: "Welcome back!",
        description: `Logged in as ${result.user.name}`,
      });
      navigate('/dashboard');
    } else {
      toast({
        title: "Login failed",
        description: result.error,
        variant: "destructive",
      });
    }
    
    setLoading(false);
  };

  const quickLogin = (role) => {
    const credentials = {
      admin: { email: 'admin@learningfwiend.com', password: 'admin123' },
      instructor: { email: 'sarah.wilson@learningfwiend.com', password: 'instructor123' },
      learner: { email: 'mike.johnson@learningfwiend.com', password: 'student123' }
    };
    
    setEmail(credentials[role].email);
    setPassword(credentials[role].password);
  };

  const handleLoginPalClick = () => {
    toast({
      title: "LoginPal Coming Soon",
      description: "LoginPal OAuth integration will be available once the service is deployed. Use the demo login options below for now.",
      variant: "default",
    });
  };

  return (
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
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
            <Button
              type="button"
              variant="outline"
              className="w-full h-12 border-2 border-indigo-200 hover:border-indigo-300 hover:bg-indigo-50 text-indigo-700 font-medium relative group"
              onClick={handleLoginPalClick}
            >
              <div className="flex items-center justify-center space-x-3">
                <div className="w-6 h-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-4 h-4 text-white" />
                </div>
                <span>Continue with LoginPal</span>
              </div>
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </Button>

            {/* Quick Login Demo Buttons */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500 text-center mb-3">Quick Demo Login:</p>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => quickLogin('admin')}
                >
                  <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                  Login as Admin
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => quickLogin('instructor')}
                >
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  Login as Instructor
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => quickLogin('learner')}
                >
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  Login as Student
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;