import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Textarea } from '../components/ui/textarea';
// TODO: Replace with backend data when final tests are implemented
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  Award,
  BookOpen,
  Trophy,
  Play,
  FileText
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const FinalTest = () => {
  const { courseId, programId } = useParams();
  const navigate = useNavigate();
  const { user, getProgramById, getCourseById, getAllCourses, updateEnrollmentProgress } = useAuth();
  const { toast } = useToast();

  // Determine if this is a program or course final test
  const isProgram = programId !== undefined;
  
  const [program, setProgram] = useState(null);
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);

  useEffect(() => {
    loadTestData();
  }, [courseId, programId, isProgram]);

  const loadTestData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (isProgram && programId) {
        // Load program data
        const programResult = await getProgramById(programId);
        if (programResult.success) {
          setProgram(programResult.program);
          
          // Also load the courses to verify completion
          if (programResult.program.courseIds?.length > 0) {
            const coursesResult = await getAllCourses();
            if (coursesResult.success) {
              const programCourses = coursesResult.courses.filter(course => 
                programResult.program.courseIds.includes(course.id)
              );
              setProgram(prev => ({ ...prev, courses: programCourses }));
            }
          }
        } else {
          setError('Program not found');
        }
      } else if (courseId) {
        // Load course data
        const courseResult = await getCourseById(courseId);
        if (courseResult.success) {
          setCourse(courseResult.course);
        } else {
          setError('Course not found');
        }
      }
    } catch (err) {
      console.error('Error loading test data:', err);
      setError('Failed to load test data');
    } finally {
      setLoading(false);
    }
  };

  const startFinalExam = () => {
    setTestStarted(true);
    toast({
      title: "Final Exam Started",
      description: "You are now taking the final exam. Good luck!",
    });
  };

  const completeFinalExam = async () => {
    // For now, we'll mark the exam as completed
    // In a real implementation, this would involve actual quiz questions
    setTestCompleted(true);
    
    // Simulate exam completion with high score
    const score = 95; // Simulated score
    
    try {
      if (isProgram && program) {
        // For program completion, we could create a program completion record
        // For now, we'll just show success
        toast({
          title: "Program Final Exam Completed!",
          description: `Congratulations! You scored ${score}% on your final exam for "${program.title}". Your certificate is being generated.`,
        });
        
        // Navigate to certificates page after a delay
        setTimeout(() => {
          navigate('/certificates');
        }, 3000);
      } else if (course) {
        // Update course progress to 100%
        const result = await updateEnrollmentProgress(course.id, {
          progress: 100
        });
        
        if (result.success) {
          toast({
            title: "Course Final Exam Completed!",
            description: `Congratulations! You scored ${score}% on your final exam for "${course.title}". Your certificate is being generated.`,
          });
          
          // Navigate to certificates page after a delay
          setTimeout(() => {
            navigate('/certificates');
          }, 3000);
        }
      }
    } catch (error) {
      console.error('Error completing final exam:', error);
      toast({
        title: "Error",
        description: "There was an error processing your exam completion.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading final exam...</p>
        </div>
      </div>
    );
  }

  if (error || (!program && isProgram) || (!course && !isProgram)) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {error || 'Exam not found'}
            </h1>
            <p className="text-gray-600 mb-6">
              {isProgram 
                ? "The program exam you're looking for could not be found."
                : "The course exam you're looking for could not be found."
              }
            </p>
            <Button onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const examTitle = isProgram ? program?.title : course?.title;
  const examType = isProgram ? "Program Final Exam" : "Course Final Exam";

  if (testCompleted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <Trophy className="h-20 w-20 text-yellow-500 mx-auto mb-6" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Congratulations! 🎉
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              You have successfully completed the final exam for "{examTitle}"
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => navigate('/certificates')}>
                <Award className="w-4 h-4 mr-2" />
                View Certificate
              </Button>
              <Button variant="outline" onClick={() => navigate('/dashboard')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (testStarted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">{examType}</CardTitle>
                <p className="text-gray-600 mt-1">{examTitle}</p>
              </div>
              <Badge variant="secondary">
                <Timer className="w-4 h-4 mr-1" />
                60:00 remaining
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Simulated Exam Interface */}
            <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
              <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Final Examination in Progress
              </h3>
              <p className="text-gray-600 mb-6">
                This is a simulated final exam interface. In a real implementation, 
                this would contain actual exam questions.
              </p>
              <p className="text-sm text-gray-500 mb-6">
                For demonstration purposes, clicking "Submit Exam" will mark the exam as completed 
                with a passing grade.
              </p>
              <Button onClick={completeFinalExam} size="lg">
                Submit Exam
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate(isProgram ? `/program/${programId}` : `/course/${courseId}`)}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to {isProgram ? 'Program' : 'Course'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="text-center">
            <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <CardTitle className="text-3xl mb-2">{examType}</CardTitle>
            <p className="text-xl text-gray-600">{examTitle}</p>
          </div>
        </CardHeader>
        <CardContent className="space-y-8">
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">
                📋 Exam Instructions
              </h3>
              <ul className="space-y-2 text-blue-800">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  This is your final examination for {isProgram ? 'the program' : 'this course'}
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  You must achieve a passing score of 70% or higher
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  Time limit: 60 minutes
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  Upon successful completion, you will receive a certificate
                </li>
              </ul>
            </CardContent>
          </Card>

          {isProgram && program && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Program Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{program.description}</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Total Courses</p>
                    <p className="text-lg font-semibold">{program.courseIds?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Program Type</p>
                    <p className="text-lg font-semibold">Comprehensive Training</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="text-center">
            <Button onClick={startFinalExam} size="lg" className="px-8">
              <Play className="w-5 h-5 mr-2" />
              Start Final Exam
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
export default FinalTest;