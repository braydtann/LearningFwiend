import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import { getImageUrl, handleImageError } from '../utils/imageUtils';
import { 
  BookOpen, 
  Clock, 
  Users, 
  Play, 
  FileText, 
  CheckCircle, 
  Star,
  ArrowLeft,
  Download,
  Presentation,
  AlertTriangle,
  Lock,
  ChevronRight,
  SkipForward,
  ClipboardCheck,
  Trophy,
  Award
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    user, 
    isLearner, 
    getCourseById, 
    getMyEnrollments, 
    updateEnrollmentProgress,
    migrateEnrollmentProgress,
    getAllPrograms,
    getAllClassrooms,
    getAllFinalTests,
    getQuizAttempts,
    getCourseQuizzes
  } = useAuth();
  const { toast } = useToast();
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [loadingEnrollments, setLoadingEnrollments] = useState(true);
  const [currentEnrollment, setCurrentEnrollment] = useState(null);
  const [nextAction, setNextAction] = useState(null); // { type: 'module'|'lesson', target: {...} }
  const [progressValue, setProgressValue] = useState(0); // Explicit progress state for UI updates
  const [enrolledPrograms, setEnrolledPrograms] = useState([]);
  const [currentProgram, setCurrentProgram] = useState(null);
  const [programCompleted, setProgramCompleted] = useState(false);
  const [showFinalExamOption, setShowFinalExamOption] = useState(false);

  // Load course data and enrollments from backend
  useEffect(() => {
    loadCourse();
    if (isLearner) {
      loadEnrollments();
      loadProgramData();
    }
  }, [id, isLearner]);

  // Calculate next action when course, enrollment, or selected lesson changes
  useEffect(() => {
    if (course && currentEnrollment && selectedLesson) {
      calculateNextAction();
    }
  }, [course, currentEnrollment, selectedLesson]);

  // Handle return from quiz - restore lesson context
  useEffect(() => {
    if (location.state?.returnFromQuiz && location.state?.lessonId && course) {
      // Find the lesson that was just completed
      let foundLesson = null;
      
      for (const module of course.modules || []) {
        if (module.lessons) {
          foundLesson = module.lessons.find(l => l.id === location.state.lessonId);
          if (foundLesson) break;
        }
      }
      
      if (foundLesson) {
        console.log(`Returning from quiz to lesson: ${foundLesson.title}`);
        setSelectedLesson(foundLesson);
        
        // Show completion message if provided
        if (location.state.message) {
          toast({
            title: "Quiz Completed",
            description: location.state.message,
            duration: 3000,
          });
        }
        
        // Clear the navigation state to prevent re-triggering
        navigate(location.pathname, { replace: true, state: {} });
      }
    }
  }, [location.state, course, navigate, toast]);

  // Update progress when enrollment changes - THIS IS THE KEY FIX
  useEffect(() => {
    if (course && currentEnrollment) {
      const newProgress = calculateProgress();
      console.log(`Progress update triggered: ${newProgress}%`);
      console.log('Current enrollment data:', JSON.stringify(currentEnrollment.moduleProgress, null, 2));
      setProgressValue(newProgress);
      
      // Also recalculate next action when progress changes
      if (selectedLesson) {
        calculateNextAction();
      }
    }
  }, [course, currentEnrollment, selectedLesson]); // Watch for enrollment AND selected lesson changes

  const loadCourse = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getCourseById(id);
      if (result.success) {
        setCourse(result.course);
      } else {
        setError(result.error || 'Course not found');
      }
    } catch (error) {
      console.error('Error loading course:', error);
      setError('Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const loadEnrollments = async () => {
    setLoadingEnrollments(true);
    console.log('🔄 Starting enrollment loading for course:', id);
    try {
      const result = await getMyEnrollments();
      console.log('📊 Enrollment API result:', result);
      if (result.success) {
        setEnrollments(result.enrollments);
        
        // Find current enrollment for this course
        const enrollment = result.enrollments.find(e => e.courseId === id);
        console.log('🎯 Found enrollment for course:', enrollment ? 'Yes' : 'No', enrollment?.id);
        if (enrollment) {
          // Check if enrollment needs migration (missing moduleProgress)
          if (!enrollment.moduleProgress || enrollment.moduleProgress.length === 0) {
            console.log('Legacy enrollment detected - migrating to new progress system...');
            const migrationResult = await migrateEnrollmentProgress(enrollment.id);
            
            if (migrationResult.success) {
              console.log('Enrollment migration successful:', migrationResult.result);
              toast({
                title: "Progress tracking updated",
                description: "Your course progress has been upgraded to the new tracking system.",
              });
              
              // Reload enrollments after migration
              const updatedResult = await getMyEnrollments();
              if (updatedResult.success) {
                const updatedEnrollment = updatedResult.enrollments.find(e => e.courseId === id);
                setCurrentEnrollment(updatedEnrollment || null);
                setEnrollments(updatedResult.enrollments);
              }
            } else {
              console.error('Failed to migrate enrollment:', migrationResult.error);
              setCurrentEnrollment(enrollment);
            }
          } else {
            setCurrentEnrollment(enrollment);
          }
        } else {
          setCurrentEnrollment(null);
        }
      } else {
        console.error('Failed to load enrollments:', result.error);
        setEnrollments([]);
        setCurrentEnrollment(null);
      }
    } catch (error) {
      console.error('Error loading enrollments:', error);
      setEnrollments([]);
      setCurrentEnrollment(null);
    } finally {
      setLoadingEnrollments(false);
    }
  };

  const loadProgramData = async () => {
    if (!isLearner || !user) return;
    
    try {
      // Get student's classrooms
      const classroomsResult = await getAllClassrooms();
      if (!classroomsResult.success) return;
      
      // Get all programs
      const programsResult = await getAllPrograms();
      if (!programsResult.success) return;
      
      // Find classrooms where student is enrolled
      const studentClassrooms = classroomsResult.classrooms.filter(classroom => 
        classroom.studentIds && classroom.studentIds.includes(user.id)
      );
      
      // Extract program IDs from student's classrooms
      const programIds = new Set();
      studentClassrooms.forEach(classroom => {
        if (classroom.programIds) {
          classroom.programIds.forEach(pid => programIds.add(pid));
        }
      });
      
      // Get program details for enrolled programs
      const enrolledPrograms = programsResult.programs.filter(program => 
        programIds.has(program.id)
      );
      
      setEnrolledPrograms(enrolledPrograms);
      
      // Find the program that contains the current course
      const currentProgram = enrolledPrograms.find(program => 
        program.courseIds && program.courseIds.includes(id)
      );
      
      setCurrentProgram(currentProgram);
      
      // Check if program is completed (if we found the current program)
      if (currentProgram) {
        await checkProgramCompletion(currentProgram);
      }
      
    } catch (error) {
      console.error('Error loading program data:', error);
    }
  };

  const checkProgramCompletion = async (program) => {
    if (!program || !program.courseIds) return;
    
    try {
      // Get current enrollments
      const enrollmentsResult = await getMyEnrollments();
      if (!enrollmentsResult.success) return;
      
      const enrollments = enrollmentsResult.enrollments;
      
      // Check completion status for each course in the program
      let completedCourses = 0;
      let totalCourses = program.courseIds.length;
      
      for (const courseId of program.courseIds) {
        const enrollment = enrollments.find(e => e.courseId === courseId);
        if (enrollment && enrollment.progress >= 100) {
          completedCourses++;
        }
      }
      
      // Only consider program completed when ALL courses are 100% complete
      const isProgramCompleted = completedCourses === totalCourses;
      

      
      setProgramCompleted(isProgramCompleted);
      
      // Check if final exam exists for this program - only when actually completed
      if (isProgramCompleted) {
        const finalTestsResult = await getAllFinalTests({ 
          program_id: program.id, 
          published_only: true 
        });
        
        if (finalTestsResult.success && finalTestsResult.tests.length > 0) {
          setShowFinalExamOption(true);
        } else {
          setShowFinalExamOption(false);
        }
      } else {
        setShowFinalExamOption(false);
      }
      
    } catch (error) {
      console.error('Error checking program completion:', error);
    }
  };

  // Calculate real progress based on enrollment data
  const calculateProgress = () => {
    return calculateProgressFromEnrollment(currentEnrollment);
  };

  // Helper function to calculate progress from any enrollment object
  const calculateProgressFromEnrollment = (enrollment) => {
    if (!enrollment || !course) return 0;
    
    // First try to calculate from moduleProgress (most accurate)
    if (enrollment.moduleProgress && course.modules) {
      const totalLessons = course.modules.reduce((total, module) => 
        total + (module.lessons?.length || 0), 0);
      
      if (totalLessons === 0) return 0;
      
      const completedLessons = enrollment.moduleProgress.reduce((total, moduleProgress) => 
        total + (moduleProgress.lessons?.filter(l => l.completed).length || 0), 0);
      
      const calculatedProgress = Math.round((completedLessons / totalLessons) * 100);
      console.log(`Progress calculation: ${completedLessons}/${totalLessons} = ${calculatedProgress}%`);
      return calculatedProgress;
    }
    
    // Fallback to backend progress if available
    if (enrollment.progress !== undefined && enrollment.progress !== null) {
      console.log(`Using backend progress: ${enrollment.progress}%`);
      return Math.round(enrollment.progress);
    }
    
    // For legacy enrollments without moduleProgress, initialize with 0
    console.log('Legacy enrollment detected - moduleProgress missing. Progress will be calculated as lessons are completed.');
    return 0;
  };

  // Calculate next action (next lesson, next module, or complete course)
  const calculateNextAction = () => {
    if (!course?.modules || !selectedLesson) {
      console.log('calculateNextAction: Missing course modules or selectedLesson');
      setNextAction(null);
      return;
    }
    
    console.log(`calculateNextAction: Course has ${course.modules.length} modules`);
    console.log(`calculateNextAction: Selected lesson: ${selectedLesson.title} (ID: ${selectedLesson.id})`);
    
    // Find current module and lesson
    let currentModuleIndex = -1;
    let currentLessonIndex = -1;
    
    for (let mi = 0; mi < course.modules.length; mi++) {
      const module = course.modules[mi];
      console.log(`calculateNextAction: Checking module ${mi}: ${module.title} (${module.lessons?.length || 0} lessons)`);
      if (module.lessons) {
        for (let li = 0; li < module.lessons.length; li++) {
          if (module.lessons[li].id === selectedLesson.id) {
            currentModuleIndex = mi;
            currentLessonIndex = li;
            console.log(`calculateNextAction: Found current lesson at module ${mi}, lesson ${li}`);
            break;
          }
        }
        if (currentModuleIndex !== -1) break;
      }
    }
    
    if (currentModuleIndex === -1) {
      console.log('calculateNextAction: Could not find current lesson in any module');
      setNextAction(null);
      return;
    }
    
    const currentModule = course.modules[currentModuleIndex];
    const isLastModule = currentModuleIndex === course.modules.length - 1;
    const isLastLessonInModule = currentLessonIndex === currentModule.lessons.length - 1;
    
    console.log(`calculateNextAction: Current module: ${currentModule.title} (${currentModuleIndex}/${course.modules.length - 1})`);
    console.log(`calculateNextAction: Current lesson: ${currentLessonIndex}/${currentModule.lessons.length - 1} in module`);
    console.log(`calculateNextAction: Is last module: ${isLastModule}, Is last lesson in module: ${isLastLessonInModule}`);
    
    // Check if this is the very last lesson in the course
    if (isLastModule && isLastLessonInModule) {
      // Calculate how many lessons are still incomplete
      const totalLessons = course.modules.reduce((total, module) => 
        total + (module.lessons?.length || 0), 0);
      
      let completedLessons = 0;
      if (currentEnrollment?.moduleProgress) {
        completedLessons = currentEnrollment.moduleProgress.reduce((total, mp) => 
          total + mp.lessons.filter(l => l.completed).length, 0);
      }
      
      console.log(`Complete Course DEBUG: Total lessons: ${totalLessons}, Already completed: ${completedLessons}`);
      
      // Check if current lesson is completed
      const currentLessonCompleted = isLessonCompleted(selectedLesson.id);
      console.log(`Current lesson "${selectedLesson.title}" completed: ${currentLessonCompleted}`);
      
      // If we complete this current lesson, how many total would be completed?
      const potentialCompletedCount = currentLessonCompleted ? completedLessons : completedLessons + 1;
      const allLessonsWillBeCompleted = potentialCompletedCount >= totalLessons;
      const remainingLessons = Math.max(0, totalLessons - potentialCompletedCount);
      
      console.log(`Potential completed count: ${potentialCompletedCount}, Can complete: ${allLessonsWillBeCompleted}, Remaining: ${remainingLessons}`);
      
      setNextAction({
        type: 'complete',
        target: null,
        moduleIndex: currentModuleIndex,
        lessonIndex: currentLessonIndex,
        canComplete: allLessonsWillBeCompleted,
        remainingLessons: remainingLessons
      });
      return;
    }
    
    // Check if there's a next lesson in current module
    if (currentLessonIndex < currentModule.lessons.length - 1) {
      const nextLesson = currentModule.lessons[currentLessonIndex + 1];
      console.log(`calculateNextAction: Next lesson in current module: ${nextLesson.title}`);
      setNextAction({
        type: 'lesson',
        target: nextLesson,
        moduleIndex: currentModuleIndex,
        lessonIndex: currentLessonIndex + 1
      });
      return;
    }
    
    // Check if there's a next module
    if (currentModuleIndex < course.modules.length - 1) {
      const nextModule = course.modules[currentModuleIndex + 1];
      console.log(`calculateNextAction: Checking next module: ${nextModule.title} (${nextModule.lessons?.length || 0} lessons)`);
      if (nextModule.lessons && nextModule.lessons.length > 0) {
        console.log(`calculateNextAction: Moving to next module: ${nextModule.title}, first lesson: ${nextModule.lessons[0].title}`);
        setNextAction({
          type: 'module',
          target: nextModule.lessons[0],
          moduleIndex: currentModuleIndex + 1,
          lessonIndex: 0,
          nextModuleTitle: nextModule.title
        });
        return;
      }
    }
    
    // No next action available
    console.log('calculateNextAction: No next action available');
    setNextAction(null);
  };

  // Check if user is enrolled using real backend data
  const isEnrolled = isLearner && currentEnrollment;
  // Get calculated progress from state instead of calculating during render
  const progress = progressValue;

  // Allow access to enrolled courses - classroom restrictions can be added later  
  const canAccessCourse = !isLearner || isEnrolled;

  // Mark lesson as complete and update progress
  // Check if student has passed required quizzes for course completion
  const checkQuizRequirements = async () => {
    try {
      // Check for quiz lessons directly in the course data
      if (!course || !course.modules) {
        console.log('No course or modules data available');
        return { passed: true, message: 'Course data not available for quiz validation' };
      }
      
      // Find all quiz lessons in the course
      const quizLessons = [];
      course.modules.forEach(module => {
        if (module.lessons) {
          module.lessons.forEach(lesson => {
            if (lesson.type === 'quiz') {
              quizLessons.push(lesson);
            }
          });
        }
      });
      
      console.log('Quiz lessons found in course:', quizLessons.length);
      
      if (quizLessons.length === 0) {
        console.log('No quiz lessons found - allowing course completion');
        return { passed: true, message: 'No quizzes required for this course' };
      }
      
      // Get student's quiz attempts  
      const attemptsResult = await getQuizAttempts(user.id);
      if (!attemptsResult.success) {
        console.error('Failed to fetch quiz attempts:', attemptsResult.error);
        return { passed: true, message: 'Could not verify quiz completion - allowing completion' }; // Default to allow completion
      }
      
      const userAttempts = attemptsResult.attempts || [];
      console.log('User quiz attempts:', userAttempts.length);
      
      // Check each quiz requirement
      const failedQuizzes = [];
      
      for (const quizLesson of quizLessons) {
        // For lesson-based quizzes, we need to check if they have a passing score requirement
        // If no passing score is defined, we assume the quiz is just for practice
        if (!quizLesson.passingScore) {
          console.log(`Quiz "${quizLesson.title}" has no passing score requirement - skipping validation`);
          continue;
        }
        
        // Find the best attempt for this quiz lesson
        const quizAttempts = userAttempts.filter(attempt => 
          attempt.lessonId === quizLesson.id || attempt.quizId === quizLesson.id
        );
        const bestAttempt = quizAttempts.reduce((best, current) => {
          return (!best || current.score > best.score) ? current : best;
        }, null);
        
        console.log(`Quiz "${quizLesson.title}": Best score = ${bestAttempt?.score || 0}%, Passing score = ${quizLesson.passingScore}%`);
        
        if (!bestAttempt || bestAttempt.score < quizLesson.passingScore) {
          failedQuizzes.push({
            title: quizLesson.title,
            bestScore: bestAttempt?.score || 0,
            passingScore: quizLesson.passingScore
          });
        }
      }
      
      if (failedQuizzes.length > 0) {
        const failedList = failedQuizzes.map(quiz => 
          `• ${quiz.title} (Scored: ${quiz.bestScore}%, Required: ${quiz.passingScore}%)`
        ).join('\n');
        
        return { 
          passed: false, 
          message: `Complete these quizzes with passing scores:\n${failedList}` 
        };
      }
      
      console.log('All quiz requirements met - allowing course completion');
      return { passed: true, message: 'All quiz requirements completed' };
      
    } catch (error) {
      console.error('Error checking quiz requirements:', error);
      return { passed: true, message: 'Could not verify quiz requirements - allowing completion' }; // Default to allow completion
    }
  };

  const markLessonComplete = async (lessonId) => {
    if (!currentEnrollment || !course) return;
    
    try {
      // Find the lesson and module
      let moduleId = null;
      let lesson = null;
      
      for (const module of course.modules || []) {
        const foundLesson = module.lessons?.find(l => l.id === lessonId);
        if (foundLesson) {
          lesson = foundLesson;
          moduleId = module.id;
          break;
        }
      }
      
      if (!lesson || !moduleId) return;
      
      // Update enrollment progress
      const moduleProgress = currentEnrollment.moduleProgress || [];
      let targetModuleProgress = moduleProgress.find(m => m.moduleId === moduleId);
      
      if (!targetModuleProgress) {
        targetModuleProgress = {
          moduleId: moduleId,
          lessons: [],
          completed: false,
          completedAt: null
        };
        moduleProgress.push(targetModuleProgress);
      }
      
      // Update lesson progress
      let lessonProgress = targetModuleProgress.lessons.find(l => l.lessonId === lessonId);
      if (!lessonProgress) {
        lessonProgress = {
          lessonId: lessonId,
          completed: false,
          completedAt: null,
          timeSpent: 0
        };
        targetModuleProgress.lessons.push(lessonProgress);
      }
      
      // Check if current lesson is already completed before marking it
      if (lessonProgress.completed) {
        toast({
          title: "Already completed!",
          description: `"${lesson.title}" is already marked as complete.`,
        });
        // Even if already completed, refresh state to ensure UI is consistent
        await loadEnrollments();
        return;
      }
      
      lessonProgress.completed = true;
      lessonProgress.completedAt = new Date().toISOString();
      
      // Check if module is complete
      const moduleFromCourse = course.modules.find(m => m.id === moduleId);
      const moduleLessons = moduleFromCourse?.lessons || [];
      const completedLessonsInModule = targetModuleProgress.lessons.filter(l => l.completed);
      
      if (completedLessonsInModule.length === moduleLessons.length) {
        targetModuleProgress.completed = true;
        targetModuleProgress.completedAt = new Date().toISOString();
      }
      
      // Calculate overall progress (including the lesson we just marked as complete)
      const totalLessons = course.modules.reduce((total, module) => 
        total + (module.lessons?.length || 0), 0);
      
      // Count all completed lessons including the one we just marked
      const totalCompletedLessons = moduleProgress.reduce((total, mp) => 
        total + mp.lessons.filter(l => l.completed).length, 0);
      
      const overallProgress = totalLessons > 0 ? (totalCompletedLessons / totalLessons) * 100 : 0;
      
      console.log(`Progress DEBUG: Total lessons: ${totalLessons}, Completed: ${totalCompletedLessons}, Progress: ${overallProgress}%`);
      console.log('Module progress data:', JSON.stringify(moduleProgress, null, 2));
      
      // Update progress in backend
      const result = await updateEnrollmentProgress(id, {
        progress: overallProgress,
        currentLessonId: lessonId,
        currentModuleId: moduleId,
        moduleProgress: moduleProgress,
        lastAccessedAt: new Date().toISOString()
      });
      
      if (result.success) {
        // Update local state with immediate effect
        const updatedEnrollment = result.enrollment;
        setCurrentEnrollment(updatedEnrollment);
        
        // Force immediate progress recalculation and UI update
        const newProgress = calculateProgressFromEnrollment(updatedEnrollment);
        console.log(`Forced progress update after lesson completion: ${newProgress}%`);
        setProgressValue(newProgress);
        
        // Check if course is fully completed (100% progress)
        if (newProgress >= 100) {
          // Check quiz requirements before allowing course completion
          const quizCheck = await checkQuizRequirements();
          
          if (!quizCheck.passed) {
            // Reset progress to 99% if quiz requirements not met
            const restrictedResult = await updateEnrollmentProgress(id, {
              progress: 99,
              currentLessonId: lessonId,
              currentModuleId: moduleId,
              moduleProgress: moduleProgress,
              lastAccessedAt: new Date().toISOString()
            });
            
            if (restrictedResult.success) {
              setCurrentEnrollment(restrictedResult.enrollment);
              setProgressValue(99);
            }
            
            toast({
              title: "Quiz Requirements Not Met",
              description: quizCheck.message,
              variant: "destructive",
              duration: 8000,
            });
            
            return; // Exit early without showing course completion
          }
        }
        
        // Force recalculation of next action with updated enrollment
        setTimeout(async () => {
          console.log('Recalculating next action after lesson completion...');
          calculateNextAction();
          
          // Double-check progress calculation
          const recomputedProgress = calculateProgressFromEnrollment(updatedEnrollment);
          if (recomputedProgress !== newProgress) {
            console.log(`Secondary progress verification: ${recomputedProgress}%`);
            setProgressValue(recomputedProgress);
          }
          
          // If course is 100% complete and quiz requirements are met, trigger linear navigation
          if (recomputedProgress >= 100) {
            console.log('Course 100% complete with quiz requirements met, checking linear navigation...');
            
            // Check if this course is part of a program and has next course
            if (currentProgram && currentProgram.courseIds) {
              const nextCourseId = getNextCourseInProgram();
              
              console.log('Linear navigation debug:', {
                currentProgram: currentProgram.title,
                currentCourseId: id,
                currentCourseIndex: currentProgram.courseIds.indexOf(id),
                nextCourseId,
                totalCourses: currentProgram.courseIds.length
              });
              
              if (nextCourseId) {
                // Show linear navigation dialog
                const shouldStartNextCourse = window.confirm(
                  `🎉 Course completed! Great job!\n\n📚 This is part of the "${currentProgram.title}" program.\n\nNext up: Continue to the next course in your learning path!\n\n▶️ Click 'OK' to start the next course immediately\n🏠 Click 'Cancel' to return to your learning path`
                );
                
                if (shouldStartNextCourse) {
                  toast({
                    title: "🚀 Continuing to next course!",
                    description: "Taking you to the next course in your program...",
                    duration: 2000,
                  });
                  // Navigate immediately to next course
                  setTimeout(() => {
                    navigate(`/course/${nextCourseId}`);
                  }, 1000);
                } else {
                  toast({
                    title: "Course completed!",
                    description: "Return to your learning path to continue.",
                    duration: 2000,
                  });
                  // Navigate to program detail (learning path view)
                  setTimeout(() => {
                    navigate(`/program/${currentProgram.id}`);
                  }, 1500);
                }
              } else {
                // All courses in program completed
                const shouldGoToProgram = window.confirm(
                  `🎉 Course completed! Great job!\n\n✅ You've finished this course in the "${currentProgram.title}" program.\n\nReturn to your learning path to see your program progress and take the final exam if available.\n\nClick 'OK' to go to your learning path.`
                );
                
                if (shouldGoToProgram) {
                  setTimeout(() => {
                    navigate(`/program/${currentProgram.id}`);
                  }, 1500);
                }
              }
            }
          }
        }, 100);
        
        // Show success message with progress update  
        const completionMessage = overallProgress >= 100 
          ? "🎉 Congratulations! You've completed the entire course!"
          : `Great job! Course progress: ${Math.round(newProgress)}%`;
        
        toast({
          title: "Lesson completed!",
          description: completionMessage,
          duration: 3000,
        });
        
        // Note: No need to call loadEnrollments() here as setCurrentEnrollment above already updates the state
        // and calculateProgress() will use the updated enrollment data immediately
      } else {
        toast({
          title: "Error",
          description: "Failed to update progress. Please try again.",
          variant: "destructive",
        });
        console.error('Failed to update progress:', result.error);
      }
    } catch (error) {
      console.error('Error marking lesson complete:', error);
      toast({
        title: "Error",
        description: "An error occurred while updating progress.",
        variant: "destructive",
      });
    }
  };

  // Handle next module/lesson navigation or course completion
  const handleNextAction = async () => {
    if (!nextAction || !selectedLesson) return;
    
    try {
      // First mark current lesson as complete (this will update progress and state)
      await markLessonComplete(selectedLesson.id);
      
      // Handle different action types
      if (nextAction.type === 'complete') {
        // Complete the course
        const result = await updateEnrollmentProgress(id, {
          progress: 100,
          currentLessonId: selectedLesson.id,
          currentModuleId: nextAction.moduleIndex,
          lastAccessedAt: new Date().toISOString()
        });
        
        if (result.success) {
          setCurrentEnrollment(result.enrollment);
          
          // Check if this course completion completes the entire program
          if (currentProgram) {
            await checkProgramCompletion(currentProgram);
          }
          
          // Show completion modal with options based on context
          if (programCompleted && showFinalExamOption) {
            // Program completed - offer final exam or dashboard
            const shouldTakeFinalExam = window.confirm(
              "🎉 Congratulations! You've completed all courses in this program!\n\nWould you like to take the final exam now, or return to your dashboard?\n\nClick 'OK' to take the final exam, or 'Cancel' to return to dashboard."
            );
            
            if (shouldTakeFinalExam) {
              navigate(`/final-test/program/${currentProgram.id}`);
            } else {
              navigate('/dashboard');
            }
          } else if (currentProgram && currentProgram.courseIds) {
            // Check if there are more courses in the program
            const nextCourseId = getNextCourseInProgram();
            
            console.log('Linear navigation debug:', {
              currentProgram: currentProgram.title,
              currentCourseId: id,
              currentCourseIndex: currentProgram.courseIds.indexOf(id),
              nextCourseId,
              totalCourses: currentProgram.courseIds.length
            });
            
            if (nextCourseId) {
              // More intuitive modal for continuing to next course
              const shouldStartNextCourse = window.confirm(
                `🎉 Course completed! Great job!\n\n📚 This is part of the "${currentProgram.title}" program.\n\nNext up: Continue to the next course in your learning path!\n\n▶️ Click 'OK' to start the next course immediately\n🏠 Click 'Cancel' to return to your dashboard`
              );
              
              if (shouldStartNextCourse) {
                toast({
                  title: "🚀 Continuing to next course!",
                  description: "Taking you to the next course in your program...",
                  duration: 2000,
                });
                // Navigate immediately to next course
                setTimeout(() => {
                  navigate(`/course/${nextCourseId}`);
                }, 1000);
              } else {
                toast({
                  title: "Course completed!",
                  description: "Return to your dashboard to continue your learning journey.",
                  duration: 2000,
                });
                setTimeout(() => {
                  navigate('/dashboard');
                }, 1500);
              }
            } else {
              // No more courses in program - but still enrolled in program
              const shouldGoToDashboard = window.confirm(
                `🎉 Course completed! Great job!\n\n✅ You've finished this course in the "${currentProgram.title}" program.\n\nReturn to your dashboard to see your program progress and unlock the final exam when all courses are complete.\n\nClick 'OK' to go to dashboard.`
              );
              
              if (shouldGoToDashboard) {
                navigate('/dashboard');
              }
            }
          } else {
            // Standalone course - offer certificates or dashboard
            const shouldViewCertificates = window.confirm(
              "🎉 Congratulations! You've completed the entire course!\n\nWould you like to view your certificates, or return to your dashboard?\n\nClick 'OK' to view certificates, or 'Cancel' to return to dashboard."
            );
            
            if (shouldViewCertificates) {
              navigate('/certificates');
            } else {
              navigate('/dashboard');
            }
          }
        }
      } else {
        // Navigate to next lesson/module
        setSelectedLesson(nextAction.target);
        
        const actionType = nextAction.type === 'module' ? 'module' : 'lesson';
        const nextTitle = nextAction.type === 'module' ? nextAction.nextModuleTitle : nextAction.target.title;
        
        // Recalculate next action for the new lesson
        setTimeout(() => {
          console.log('Recalculating next action after navigation...');
          calculateNextAction();
        }, 100);
        
        toast({
          title: `Moving to next ${actionType}!`,
          description: `Now starting: ${nextTitle}`,
        });
      }
    } catch (error) {
      console.error('Error handling next action:', error);
      toast({
        title: "Error",
        description: "An error occurred while processing your request.",
        variant: "destructive",
      });
    }
  };

  // Check if lesson is completed
  const isLessonCompleted = (lessonId) => {
    if (!currentEnrollment?.moduleProgress) return false;
    
    for (const moduleProgress of currentEnrollment.moduleProgress) {
      const lessonProgress = moduleProgress.lessons?.find(l => l.lessonId === lessonId);
      if (lessonProgress?.completed) return true;
    }
    return false;
  };

  // For now, set basic progress - this can be enhanced later with real progress tracking
  // const progress = 0; // TODO: Implement real progress tracking

  // Loading state - prioritize course loading over enrollment loading
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Loading course...</h3>
        <p className="text-gray-600">Please wait while we fetch the course details.</p>
      </div>
    );
  }

  // Error or course not found
  if (error || !course) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-16 w-16 text-orange-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Course Not Available
        </h1>
        <p className="text-gray-600 mb-6">
          {error || 'This course is no longer available or may have been removed.'}
        </p>
        <div className="space-x-4">
          <Button onClick={() => navigate('/courses')}>
            Browse All Courses
          </Button>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  // Check access for learners - they need to be enrolled
  if (isLearner && !canAccessCourse) {
    return (
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-6">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => navigate('/courses')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="h-6 border-l border-gray-300"></div>
          <nav className="text-sm text-gray-500">
            <span>Courses</span> / <span className="text-gray-900">{course?.title || 'Loading...'}</span>
          </nav>
        </div>

        {/* Access Denied */}
        <Card className="max-w-2xl mx-auto">
          <CardContent className="text-center py-12">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Lock className="w-10 h-10 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Course Access Restricted</h2>
            <p className="text-gray-600 mb-6">
              You need to be enrolled in this course to access its content.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Enrollment Required</p>
                  <p className="text-sm text-yellow-700">
                    Please contact your instructor to get enrolled in this course.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <Button onClick={() => navigate('/courses')} variant="outline">
                Browse Other Courses
              </Button>
              <p className="text-xs text-gray-500">
                Contact your instructor if you believe this is an error
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleEnroll = () => {
    toast({
      title: "Enrolled successfully!",
      description: "You can now access all course materials.",
    });
  };

  const handleLessonClick = (lesson) => {
    if (lesson.type === 'quiz') {
      // Check if quiz data exists
      if (!lesson.quiz || !lesson.quiz.questions || lesson.quiz.questions.length === 0) {
        toast({
          title: "Quiz not available",
          description: "This quiz hasn't been set up yet. Please contact your instructor.",
          variant: "destructive",
        });
        return;
      }
      
      // Navigate to quiz taking page
      navigate(`/quiz/${id}/${lesson.id}`);
    } else {
      setSelectedLesson(lesson);
    }
  };

  // Helper function to check if student can access a quiz based on their progress
  const canAccessQuiz = (quiz) => {
    if (!currentEnrollment || !currentEnrollment.moduleProgress || !course?.modules) {
      return false; // No progress data available
    }

    // Check if student has actually started the course (has any lesson progress)
    const hasAnyProgress = currentEnrollment.moduleProgress.some(mp => 
      mp.lessons && mp.lessons.length > 0 && mp.lessons.some(l => l.completed)
    );
    
    if (!hasAnyProgress) {
      return false; // Student hasn't started the course yet
    }

    // Find which module contains this quiz
    let quizModuleIndex = -1;
    let quizLessonIndex = -1;
    
    for (let i = 0; i < course.modules.length; i++) {
      const module = course.modules[i];
      if (module.lessons) {
        for (let j = 0; j < module.lessons.length; j++) {
          if (module.lessons[j].id === quiz.id) {
            quizModuleIndex = i;
            quizLessonIndex = j;
            break;
          }
        }
        if (quizModuleIndex !== -1) break;
      }
    }

    if (quizModuleIndex === -1 || quizLessonIndex === -1) {
      return false; // Quiz module not found
    }

    const quizModule = course.modules[quizModuleIndex];
    const moduleProgress = currentEnrollment.moduleProgress;
    
    // Check if all previous modules are completed
    for (let i = 0; i < quizModuleIndex; i++) {
      const prevModuleProgress = moduleProgress.find(mp => mp.moduleId === course.modules[i].id);
      if (!prevModuleProgress || !prevModuleProgress.completed) {
        return false; // Previous module not completed
      }
    }
    
    // Check if student has reached the quiz lesson within the current module
    const currentModuleProgress = moduleProgress.find(mp => mp.moduleId === quizModule.id);
    if (!currentModuleProgress) {
      return false; // No progress on current module
    }
    
    // Allow quiz access only if student has completed all lessons before the quiz in the same module
    const lessonsBeforeQuiz = quizModule.lessons.slice(0, quizLessonIndex);
    for (const lesson of lessonsBeforeQuiz) {
      const lessonProgress = currentModuleProgress.lessons.find(lp => lp.lessonId === lesson.id);
      if (!lessonProgress || !lessonProgress.completed) {
        return false; // Previous lesson in module not completed
      }
    }

    return true; // All prerequisites completed
  };

  // Helper function to get next course in program
  const getNextCourseInProgram = () => {
    if (!currentProgram || !currentProgram.courseIds) return null;
    
    const currentCourseIndex = currentProgram.courseIds.indexOf(id);
    if (currentCourseIndex === -1 || currentCourseIndex >= currentProgram.courseIds.length - 1) {
      return null; // No next course
    }
    
    return currentProgram.courseIds[currentCourseIndex + 1];
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => {
            if (selectedLesson) {
              // If viewing a lesson, go back to course overview
              setSelectedLesson(null);
            } else {
              // If on course overview, go back to courses list
              navigate('/courses');
            }
          }}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {selectedLesson ? 'Back to Course Overview' : 'Back'}
        </Button>
        <div className="h-6 border-l border-gray-300"></div>
        <nav className="text-sm text-gray-500">
          <span>Courses</span> / <span className="text-gray-900">{course?.title || 'Loading...'}</span>
        </nav>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {/* Main content - now full width */}
        <div className="space-y-6">
          {/* Course Header */}
          <div>
            <div className="aspect-video relative overflow-hidden rounded-lg mb-6">
              <img 
                src={getImageUrl(course.thumbnailUrl || course.thumbnail)} 
                alt={course.title}
                className="w-full h-full object-cover"
                onError={(e) => handleImageError(e)}
              />
              {(selectedLesson?.type === 'video' || selectedLesson?.type === 'presentation') && 
               (selectedLesson.videoUrl || selectedLesson.presentationUrl || selectedLesson.embedCode) && (
                <div className="absolute inset-0 bg-black">
                  {/* Back button for video/presentation */}
                  <div className="absolute top-4 left-4 z-10">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setSelectedLesson(null)}
                      className="bg-black/50 border-white/20 text-white hover:bg-black/70"
                    >
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Back to Course Overview
                    </Button>
                  </div>
                  {(() => {
                    // Handle Canva presentations with embed code (priority)
                    if (selectedLesson.type === 'presentation' && selectedLesson.embedCode) {
                      return (
                        <div 
                          className="w-full h-full"
                          dangerouslySetInnerHTML={{ __html: selectedLesson.embedCode }}
                        />
                      );
                    }
                    
                    const url = selectedLesson.videoUrl || selectedLesson.presentationUrl;
                    
                    // Handle Canva presentations with URL (fallback)
                    if (selectedLesson.type === 'presentation' || url.includes('canva.com')) {
                      // Convert Canva sharing link to embed format
                      if (url.includes('canva.com/design/')) {
                        const designId = url.match(/design\/([^\/\?]+)/)?.[1];
                        if (designId) {
                          return (
                            <iframe
                              src={`https://www.canva.com/design/${designId}/view?embed`}
                              className="w-full h-full"
                              allowFullScreen
                              title={selectedLesson.title}
                            />
                          );
                        }
                      }
                      
                      // Fallback for other Canva URLs
                      return (
                        <iframe
                          src={url.includes('?embed') ? url : `${url}?embed`}
                          className="w-full h-full"
                          allowFullScreen
                          title={selectedLesson.title}
                        />
                      );
                    }
                    
                    // Handle Google Drive links
                    if (url.includes('drive.google.com')) {
                      const fileId = url.match(/\/file\/d\/([a-zA-Z0-9-_]+)/)?.[1] || 
                                   url.match(/id=([a-zA-Z0-9-_]+)/)?.[1];
                      if (fileId) {
                        return (
                          <iframe
                            src={`https://drive.google.com/file/d/${fileId}/preview`}
                            className="w-full h-full"
                            allowFullScreen
                            title={selectedLesson.title}
                          />
                        );
                      }
                    }
                    
                    // Handle YouTube URLs - convert to embeddable format
                    if (url.includes('youtube.com/watch') || url.includes('youtu.be/')) {
                      let videoId = '';
                      
                      if (url.includes('youtube.com/watch')) {
                        const urlParams = new URLSearchParams(url.split('?')[1]);
                        videoId = urlParams.get('v');
                      } else if (url.includes('youtu.be/')) {
                        videoId = url.split('youtu.be/')[1].split('?')[0];
                      }
                      
                      if (videoId) {
                        return (
                          <iframe
                            src={`https://www.youtube.com/embed/${videoId}`}
                            className="w-full h-full"
                            allowFullScreen
                            title={selectedLesson.title}
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          />
                        );
                      }
                    }
                    
                    // Handle Vimeo URLs
                    if (url.includes('vimeo.com/')) {
                      const videoId = url.split('vimeo.com/')[1].split('?')[0];
                      if (videoId) {
                        return (
                          <iframe
                            src={`https://player.vimeo.com/video/${videoId}`}
                            className="w-full h-full"
                            allowFullScreen
                            title={selectedLesson.title}
                          />
                        );
                      }
                    }
                    
                    // Fallback for other video URLs
                    return (
                      <iframe
                        src={url}
                        className="w-full h-full"
                        allowFullScreen
                        title={selectedLesson.title}
                      />
                    );
                  })()}
                </div>
              )}
              
              {/* Text-based content display */}
              {selectedLesson?.type === 'text' && selectedLesson.content && (
                <div className="absolute inset-0 bg-white overflow-y-auto">
                  <div className="p-8">
                    <div className="max-w-4xl mx-auto">
                      <div className="mb-6">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setSelectedLesson(null)}
                          className="mb-4"
                        >
                          <ArrowLeft className="w-4 h-4 mr-2" />
                          Back to Course Overview
                        </Button>
                        <Badge variant="outline" className="mb-2">
                          Text Lesson
                        </Badge>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">
                          {selectedLesson.title}
                        </h2>
                      </div>
                      <div className="prose prose-lg prose-gray max-w-none">
                        <div 
                          className="text-gray-700 leading-relaxed whitespace-pre-wrap"
                          dangerouslySetInnerHTML={{ 
                            __html: selectedLesson.content.replace(/\n/g, '<br/>') 
                          }}
                        />
                      </div>
                      
                      {/* Document attachment display */}
                      {selectedLesson.documentUrl && selectedLesson.documentName && (
                        <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
                          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                            <FileText className="w-5 h-5 mr-2 text-blue-600" />
                            Course Documents
                          </h3>
                          <div className="bg-white p-4 rounded-lg border border-blue-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                  <FileText className="w-5 h-5 text-blue-600" />
                                </div>
                                <div>
                                  <p className="font-medium text-gray-900">{selectedLesson.documentName}</p>
                                  <p className="text-sm text-gray-500">Click to view or download</p>
                                </div>
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  // Check if it's a fake URL (old courses)
                                  if (selectedLesson.documentUrl.includes('example.com')) {
                                    toast({
                                      title: "Document not available",
                                      description: "This document was uploaded before our new system. Please contact your instructor.",
                                      variant: "destructive",
                                    });
                                  } else {
                                    // Open document in new tab for viewing/downloading
                                    window.open(selectedLesson.documentUrl, '_blank');
                                  }
                                }}
                                className="flex items-center space-x-2"
                              >
                                <Download className="w-4 h-4" />
                                <span>View Document</span>
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <Badge variant="secondary" className="mb-2">
                  {course.category}
                </Badge>
                <h1 className="text-3xl font-bold text-gray-900 mb-3">
                  {course.title}
                </h1>
                <p className="text-lg text-gray-600 mb-4">
                  {course.description}
                </p>
                <div className="flex items-center space-x-6 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Users className="w-4 h-4 mr-1" />
                    {course.enrolledStudents} students
                  </div>
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {course.duration}
                  </div>
                  <div className="flex items-center">
                    <BookOpen className="w-4 h-4 mr-1" />
                    {course.totalLessons} lessons
                  </div>
                  <div className="flex items-center">
                    <Star className="w-4 h-4 mr-1 fill-yellow-400 text-yellow-400" />
                    4.8 (245 reviews)
                  </div>
                </div>
              </div>
            </div>

            {/* Progress Section - only for enrolled students */}
            {isEnrolled && (
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-700">Your Progress</span>
                  <span className="text-sm font-bold text-blue-700">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            )}

            {/* Quick Quiz Access - only for enrolled students */}
            {isEnrolled && course?.modules && (
              (() => {
                // Find all quiz lessons across all modules
                const quizLessons = [];
                course.modules.forEach((module, moduleIndex) => {
                  if (module.lessons) {
                    module.lessons.forEach((lesson, lessonIndex) => {
                      if (lesson.type === 'quiz') {
                        quizLessons.push({
                          ...lesson,
                          moduleTitle: module.title,
                          moduleIndex,
                          lessonIndex
                        });
                      }
                    });
                  }
                });

                if (quizLessons.length > 0) {
                  // Filter quizzes based on progressive access
                  const accessibleQuizzes = quizLessons.filter(quiz => canAccessQuiz(quiz));
                  const lockedQuizzes = quizLessons.filter(quiz => !canAccessQuiz(quiz));

                  return (
                    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-lg mb-6 border border-purple-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900 mb-2">
                            <ClipboardCheck className="w-6 h-6 inline mr-2 text-purple-600" />
                            Course Quizzes
                          </h3>
                          <p className="text-gray-600 mb-3">
                            {accessibleQuizzes.length > 0 ? (
                              <>Available: {accessibleQuizzes.length} quiz{accessibleQuizzes.length > 1 ? 'es' : ''}</>
                            ) : (
                              <>Complete previous modules to unlock quizzes</>
                            )}
                            {lockedQuizzes.length > 0 && (
                              <span className="text-sm text-gray-500 ml-2">
                                ({lockedQuizzes.length} locked)
                              </span>
                            )}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {/* Show accessible quizzes */}
                            {accessibleQuizzes.slice(0, 3).map((quiz) => (
                              <Button
                                key={quiz.id}
                                variant="outline"
                                size="sm"
                                className="bg-white border-purple-300 text-purple-700 hover:bg-purple-50"
                                onClick={() => {
                                  navigate(`/quiz/${id}/${quiz.id}`);
                                }}
                              >
                                <ClipboardCheck className="w-4 h-4 mr-1" />
                                {quiz.title}
                              </Button>
                            ))}
                            
                            {/* Show locked quizzes (disabled) */}
                            {lockedQuizzes.slice(0, Math.max(0, 3 - accessibleQuizzes.length)).map((quiz) => (
                              <Button
                                key={quiz.id}
                                variant="outline"
                                size="sm"
                                className="bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed"
                                disabled
                                title={`Complete previous modules to unlock this quiz`}
                              >
                                <Lock className="w-4 h-4 mr-1" />
                                {quiz.title}
                              </Button>
                            ))}
                            
                            {quizLessons.length > 3 && (
                              <span className="text-sm text-gray-500 self-center">
                                +{quizLessons.length - 3} more quiz{quizLessons.length - 3 > 1 ? 'es' : ''}
                              </span>
                            )}
                          </div>
                        </div>
                        {accessibleQuizzes.length === 1 && lockedQuizzes.length === 0 && (
                          <Button 
                            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 text-lg"
                            onClick={() => {
                              navigate(`/quiz/${id}/${accessibleQuizzes[0].id}`);
                            }}
                          >
                            <ClipboardCheck className="w-5 h-5 mr-2" />
                            Start Quiz
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                }
                return null;
              })()
            )}

            {/* Start Course Button - When no lesson is selected */}
            {!selectedLesson && isEnrolled && course?.modules?.length > 0 && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg mb-6 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to start learning?</h3>
                    <p className="text-gray-600">
                      Begin your journey with the first lesson: {course.modules[0]?.lessons?.[0]?.title || 'First lesson'}
                    </p>
                  </div>
                  <Button 
                    className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 text-lg"
                    onClick={() => {
                      const firstLesson = course.modules[0]?.lessons?.[0];
                      if (firstLesson) {
                        setSelectedLesson(firstLesson);
                        toast({
                          title: "Course started!",
                          description: `Welcome to ${course.title}. Let's begin your learning journey!`,
                        });
                      }
                    }}
                  >
                    <Play className="w-5 h-5 mr-2" />
                    Start Course
                  </Button>
                </div>
              </div>
            )}

            {/* Next Module/Lesson/Complete Course Button - Below main content */}
            {selectedLesson && nextAction && isEnrolled && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg mb-6 border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {nextAction.type === 'complete' 
                        ? 'Ready to complete the course?' 
                        : 'Ready for the next step?'
                      }
                    </h3>
                    <p className="text-sm text-gray-600">
                      {nextAction.type === 'complete' 
                        ? nextAction.canComplete
                          ? 'All lessons completed! Click to finish the course and get your certificate.'
                          : `Complete ${nextAction.remainingLessons} more lesson${nextAction.remainingLessons !== 1 ? 's' : ''} to finish the course.`
                        : nextAction.type === 'module' 
                          ? `Continue to the next module: ${nextAction.nextModuleTitle}`
                          : `Move to the next lesson: ${nextAction.target.title}`
                      }
                    </p>
                  </div>
                  <Button 
                    className={`px-6 ${
                      nextAction.type === 'complete' && !nextAction.canComplete
                        ? 'bg-gray-400 hover:bg-gray-400 cursor-not-allowed text-white' 
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                    onClick={handleNextAction}
                    disabled={nextAction.type === 'complete' && !nextAction.canComplete}
                  >
                    {nextAction.type === 'complete' ? (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Complete Course
                      </>
                    ) : nextAction.type === 'module' ? (
                      <>
                        <SkipForward className="w-4 h-4 mr-2" />
                        Next Module
                      </>
                    ) : (
                      <>
                        <ChevronRight className="w-4 h-4 mr-2" />
                        Next Lesson
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
            
            {/* Final Exam Button - Show when program is completed */}
            {programCompleted && showFinalExamOption && currentProgram && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg mb-6 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
                      🎉 Program Completed!
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      Congratulations! You've completed all courses in "{currentProgram.title}".
                    </p>
                    <p className="text-sm text-green-700 font-medium">
                      You're now eligible to take the final exam to earn your certificate.
                    </p>
                  </div>
                  <Button 
                    className="px-6 bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => navigate(`/final-test/program/${currentProgram.id}`)}
                  >
                    <Award className="w-4 h-4 mr-2" />
                    Take Final Exam
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Course Content Tabs */}
          <Tabs defaultValue="curriculum" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="curriculum">Curriculum</TabsTrigger>
              <TabsTrigger value="description">Description</TabsTrigger>
            </TabsList>
            
            <TabsContent value="curriculum" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Course Content</CardTitle>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    {course.modules?.map((module, moduleIndex) => (
                      <AccordionItem key={module.id} value={module.id}>
                        <AccordionTrigger className="text-left">
                          <div className="flex items-center justify-between w-full mr-4">
                            <span className="font-medium">
                              Module {moduleIndex + 1}: {module.title}
                            </span>
                            <span className="text-sm text-gray-500">
                              {module.lessons?.length || 0} lessons
                            </span>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-3 pt-2">
                            {module.lessons?.map((lesson, lessonIndex) => {
                              const completed = isLessonCompleted(lesson.id);
                              const isCurrentLesson = selectedLesson?.id === lesson.id;
                              
                              return (
                                <div 
                                  key={lesson.id}
                                  className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
                                    isCurrentLesson
                                      ? 'bg-blue-50 border-blue-200' 
                                      : completed 
                                        ? 'bg-green-50 border-green-200'
                                        : 'hover:bg-gray-50'
                                  } ${!isEnrolled && 'opacity-50 cursor-not-allowed'}`}
                                  onClick={() => isEnrolled && handleLessonClick(lesson)}
                                >
                                  <div className="flex items-center space-x-3">
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                                      completed ? 'bg-green-100' : 'bg-gray-100'
                                    }`}>
                                      {completed ? (
                                        <CheckCircle className="w-4 h-4 text-green-600" />
                                      ) : (
                                        <>
                                          {lesson.type === 'video' && <Play className="w-4 h-4" />}
                                          {lesson.type === 'presentation' && <Presentation className="w-4 h-4" />}
                                          {lesson.type === 'text' && <FileText className="w-4 h-4" />}
                                          {lesson.type === 'quiz' && <CheckCircle className="w-4 h-4 text-purple-600" />}
                                        </>
                                      )}
                                    </div>
                                    <div>
                                      <p className={`font-medium ${completed ? 'text-green-800' : 'text-gray-900'}`}>
                                        {lessonIndex + 1}. {lesson.title}
                                        {completed && (
                                          <Badge variant="outline" className="ml-2 text-green-600 border-green-600">
                                            Completed
                                          </Badge>
                                        )}
                                        {lesson.type === 'quiz' && !completed && (
                                          <Badge variant="outline" className="ml-2 text-purple-600">
                                            Quiz
                                          </Badge>
                                        )}
                                      </p>
                                      {lesson.duration && (
                                        <p className="text-sm text-gray-500">{lesson.duration}</p>
                                      )}
                                      {lesson.type === 'quiz' && lesson.quiz && (
                                        <p className="text-sm text-gray-500">
                                          {lesson.quiz.questions?.length || 0} questions • {lesson.quiz.timeLimit || 10} min
                                        </p>
                                      )}
                                    </div>
                                  </div>
                                  
                                  {/* Action buttons - only show checkmark and remove Next Lesson button from here */}
                                  <div className="flex items-center space-x-2">
                                    {isEnrolled && !completed && (
                                      <Button 
                                        size="sm" 
                                        variant="outline"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          markLessonComplete(lesson.id);
                                        }}
                                        title="Mark as complete"
                                      >
                                        <CheckCircle className="w-4 h-4" />
                                      </Button>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="description">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-3">About this course</h3>
                      <p className="text-gray-600 leading-relaxed">
                        {course.description}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-semibold mb-3">What you'll learn</h3>
                      <ul className="space-y-2">
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Master the fundamentals and advanced concepts</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Build real-world projects from scratch</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Best practices and industry standards</span>
                        </li>
                        <li className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">Prepare for professional opportunities</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="reviews" style={{display: 'none'}}>
              {/* Hidden reviews section */}
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar - Hidden as per user request */}
        <div className="space-y-6" style={{display: 'none'}}>
          {/* Enrollment Card - Hidden */}
          <Card>
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <div className="text-3xl font-bold text-gray-900">Free</div>
                
                {isEnrolled ? (
                  <div className="space-y-3">
                    <Badge className="w-full py-2 bg-green-600">
                      ✓ Enrolled
                    </Badge>
                    <Button className="w-full" onClick={() => navigate('/dashboard')}>
                      Go to Dashboard
                    </Button>
                  </div>
                ) : (
                  <Button 
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    onClick={handleEnroll}
                  >
                    Enroll Now
                  </Button>
                )}
                
                <div className="text-xs text-gray-500 space-y-1">
                  <p>✓ Lifetime access</p>
                  <p>✓ Certificate of completion</p>
                  <p>✓ 30-day money-back guarantee</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Instructor Info - Hidden */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Instructor</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-3 mb-4">
                <img 
                  src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=60&h=60&fit=crop&crop=face" 
                  className="w-12 h-12 rounded-full object-cover"
                  alt={course.instructor}
                />
                <div>
                  <p className="font-medium text-gray-900">{course.instructor}</p>
                  <p className="text-sm text-gray-600">Senior Developer</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Expert instructor with 10+ years of experience in the field.
              </p>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span>Total Students</span>
                  <span className="font-medium">2,543</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Courses</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Rating</span>
                  <span className="font-medium">4.9/5</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Course Features - Hidden */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">This course includes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-gray-500" />
                  <span>{course.duration} of content</span>
                </div>
                <div className="flex items-center">
                  <BookOpen className="w-4 h-4 mr-2 text-gray-500" />
                  <span>{course.totalLessons} lessons</span>
                </div>
                <div className="flex items-center">
                  <Download className="w-4 h-4 mr-2 text-gray-500" />
                  <span>Downloadable resources</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-gray-500" />
                  <span>Certificate of completion</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;