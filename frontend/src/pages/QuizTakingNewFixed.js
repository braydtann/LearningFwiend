import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card.jsx';
import { Button } from '../components/ui/button.jsx';
import { Badge } from '../components/ui/badge.jsx';
import { Progress } from '../components/ui/progress.jsx';
import { Textarea } from '../components/ui/textarea.jsx';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Timer,
  BookOpen,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const QuizTakingNewFixed = () => {
  // Get URL parameters safely
  const urlParams = useParams();
  const navigate = useNavigate();
  const authContext = useAuth();
  const toastContext = useToast();
  
  // Extract values with fallbacks to prevent temporal dead zone
  const courseId = urlParams?.courseId || null;
  const lessonId = urlParams?.lessonId || null;
  const user = authContext?.user || null;
  const getCourseById = authContext?.getCourseById || null;
  const updateEnrollmentProgress = authContext?.updateEnrollmentProgress || null;
  const toast = toastContext?.toast || (() => console.log('Toast not available'));

  // All state declarations
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [initializing, setInitializing] = useState(false); // Prevent multiple concurrent initializations

  // Refs for stable references
  const isMountedRef = useRef(true);
  const timerRef = useRef(null);

  // Initialize quiz data
  const initializeQuiz = useCallback(async () => {
    if (!isMountedRef.current) return;
    
    // Prevent multiple concurrent initializations
    if (initializing) {
      console.log('Quiz initialization already in progress, skipping...');
      return;
    }
    
    try {
      setInitializing(true);
      console.log('Starting quiz initialization...');
      setLoading(true);
      setError(null);
      
      if (!courseId || !lessonId) {
        throw new Error('Missing course ID or lesson ID');
      }

      if (!getCourseById || typeof getCourseById !== 'function') {
        throw new Error('getCourseById function not available');
      }

      console.log('Loading course:', courseId);
      const courseResult = await getCourseById(courseId);
      
      if (!courseResult.success) {
        throw new Error('Failed to load course');
      }

      const courseData = courseResult.course;
      setCourse(courseData);

      // Find the lesson and quiz
      let foundLesson = null;
      let foundQuiz = null;

      // Safely iterate through modules - handle both old and new quiz structures
      if (courseData.modules && Array.isArray(courseData.modules)) {
        for (let i = 0; i < courseData.modules.length; i++) {
          const module = courseData.modules[i];
          if (module && module.lessons && Array.isArray(module.lessons)) {
            for (let j = 0; j < module.lessons.length; j++) {
              const moduleLesson = module.lessons[j];
              if (moduleLesson && moduleLesson.id === lessonId) {
                foundLesson = moduleLesson;
                if (moduleLesson.type === 'quiz') {
                  // Handle both old and new quiz structures
                  console.log('Found quiz lesson, checking structure:', {
                    lessonId: moduleLesson.id,
                    hasDirectQuestions: !!(moduleLesson.questions && Array.isArray(moduleLesson.questions)),
                    hasNestedQuestions: !!(moduleLesson.quiz && moduleLesson.quiz.questions),
                    directQuestionsLength: moduleLesson.questions ? moduleLesson.questions.length : 0,
                    nestedQuestionsLength: moduleLesson.quiz && moduleLesson.quiz.questions ? moduleLesson.quiz.questions.length : 0
                  });
                  
                  if (moduleLesson.questions && Array.isArray(moduleLesson.questions)) {
                    // New structure: questions directly on lesson
                    console.log('Using NEW quiz structure (lesson.questions)');
                    foundQuiz = {
                      questions: moduleLesson.questions,
                      timeLimit: moduleLesson.timeLimit,
                      passingScore: moduleLesson.passingScore,
                      maxAttempts: moduleLesson.maxAttempts,
                      targetQuestionCount: moduleLesson.targetQuestionCount,
                      // Copy any other quiz properties that might exist
                      ...moduleLesson.quiz
                    };
                  } else if (moduleLesson.quiz && moduleLesson.quiz.questions) {
                    // Old structure: questions nested in quiz object
                    console.log('Using OLD quiz structure (lesson.quiz.questions)');
                    foundQuiz = {
                      ...moduleLesson.quiz,
                      // Ensure all expected properties exist with defaults
                      questions: moduleLesson.quiz.questions || [],
                      timeLimit: moduleLesson.quiz.timeLimit,
                      passingScore: moduleLesson.quiz.passingScore,
                      maxAttempts: moduleLesson.quiz.maxAttempts,
                      targetQuestionCount: moduleLesson.quiz.targetQuestionCount
                    };
                  } else {
                    console.warn('Quiz lesson found but no questions structure detected:', {
                      hasQuiz: !!moduleLesson.quiz,
                      quizKeys: moduleLesson.quiz ? Object.keys(moduleLesson.quiz) : [],
                      lessonKeys: Object.keys(moduleLesson)
                    });
                  }
                }
                break;
              }
            }
          }
          if (foundLesson) break;
        }
      }

      if (!foundLesson) {
        throw new Error('Lesson not found');
      }

      if (!foundQuiz || !foundQuiz.questions || foundQuiz.questions.length === 0) {
        throw new Error('Quiz not found or has no questions');
      }
      
      console.log('Starting question validation for quiz:', {
        totalQuestions: foundQuiz.questions.length,
        questions: foundQuiz.questions.map((q, i) => ({
          index: i,
          id: q?.id,
          type: q?.type,
          question: q?.question?.substring(0, 50) + '...',
          hasOptions: !!(q?.options && Array.isArray(q.options)),
          optionsLength: q?.options?.length,
          hasCorrectAnswers: !!(q?.correctAnswers && Array.isArray(q.correctAnswers)),
          correctAnswersLength: q?.correctAnswers?.length,
          fullQuestion: q // Log the entire question object
        }))
      });
      
      // Validate each question has required structure to prevent React Error #31
      const validatedQuestions = foundQuiz.questions.filter((question, index) => {
        console.log(`Validating question ${index + 1}:`, question);
        
        if (!question || typeof question !== 'object') {
          console.warn(`❌ Question ${index + 1} FAILED: not an object:`, question);
          return false;
        }
        if (!question.type) {
          console.warn(`❌ Question ${index + 1} FAILED: missing type:`, question);
          return false;
        }
        if (!question.question || typeof question.question !== 'string' || question.question.trim() === '') {
          console.warn(`❌ Question ${index + 1} FAILED: missing or invalid question text:`, question);
          return false;
        }
        
        console.log(`Question ${index + 1} passed basic validation, checking type-specific rules for type: ${question.type}`);
        
        // Type-specific validation
        if (question.type === 'true-false') {
          // True/false questions need correctAnswer boolean
          if (typeof question.correctAnswer !== 'boolean') {
            console.warn(`❌ Question ${index + 1} FAILED: (true-false) missing valid correctAnswer:`, question.correctAnswer);
            return false;
          }
        } else if (question.type === 'multiple-choice') {
          // Multiple choice questions need options array and correctAnswer index
          if (!question.options || !Array.isArray(question.options) || question.options.length < 2) {
            console.warn(`❌ Question ${index + 1} FAILED: (multiple-choice) missing valid options array:`, question);
            return false;
          }
          if (typeof question.correctAnswer !== 'number' || question.correctAnswer < 0 || question.correctAnswer >= question.options.length) {
            console.warn(`❌ Question ${index + 1} FAILED: (multiple-choice) has invalid correctAnswer:`, question.correctAnswer);
            return false;
          }
        } else if (question.type === 'select-all-that-apply') {
          console.log(`Validating select-all-that-apply question ${index + 1}:`, {
            hasOptions: !!(question.options),
            isOptionsArray: Array.isArray(question.options),
            optionsLength: question.options ? question.options.length : 0,
            hasCorrectAnswers: !!(question.correctAnswers),
            isCorrectAnswersArray: Array.isArray(question.correctAnswers),
            correctAnswersLength: question.correctAnswers ? question.correctAnswers.length : 0
          });
          
          // Select all questions need options array and correctAnswers array
          if (!question.options || !Array.isArray(question.options) || question.options.length < 2) {
            console.warn(`❌ Question ${index + 1} FAILED: (select-all-that-apply) missing valid options array:`, question);
            return false;
          }
          
          // Initialize correctAnswers if it doesn't exist or isn't an array
          if (!question.correctAnswers || !Array.isArray(question.correctAnswers)) {
            question.correctAnswers = [];
            console.warn(`⚠️ Question ${index + 1} (select-all-that-apply) missing correctAnswers array, initializing as empty:`, question.correctAnswers);
          }
          
          // Allow empty correctAnswers (no correct answers marked) but warn about it
          if (question.correctAnswers.length === 0) {
            console.warn(`⚠️ Question ${index + 1} (select-all-that-apply) has no correct answers marked - will be unscorable:`, question.correctAnswers);
          }
          
          // Validate that any existing correctAnswers indices are within options range
          if (question.correctAnswers.length > 0) {
            const invalidIndices = question.correctAnswers.filter(idx => 
              typeof idx !== 'number' || idx < 0 || idx >= question.options.length
            );
            if (invalidIndices.length > 0) {
              console.warn(`❌ Question ${index + 1} FAILED: (select-all-that-apply) has invalid correctAnswers indices:`, invalidIndices);
              return false;
            }
          }
        } else if (question.type === 'chronological-order') {
          console.log(`🔍 CHRONOLOGICAL ORDER VALIDATION - Question ${index + 1}:`, {
            questionId: question.id,
            questionText: question.question,
            hasItems: !!(question.items),
            isItemsArray: Array.isArray(question.items),
            itemsLength: question.items ? question.items.length : 0,
            itemsContent: question.items ? question.items.map((item, idx) => ({
              index: idx,
              type: typeof item,
              text: typeof item === 'string' ? item : (item?.text || 'NO TEXT'),
              hasImage: !!(typeof item === 'object' && item?.image),
              hasAudio: !!(typeof item === 'object' && item?.audio)
            })) : 'NO ITEMS',
            hasCorrectOrder: !!(question.correctOrder),
            isCorrectOrderArray: Array.isArray(question.correctOrder),
            correctOrderLength: question.correctOrder ? question.correctOrder.length : 0,
            correctOrderContent: question.correctOrder || 'NO CORRECT ORDER'
          });
          
          // Chronological order questions need items array and correctOrder array
          if (!question.items || !Array.isArray(question.items) || question.items.length < 2) {
            console.error(`❌ CHRONOLOGICAL ORDER VALIDATION FAILED - Question ${index + 1}: missing valid items array`, {
              hasItems: !!(question.items),
              isArray: Array.isArray(question.items),
              length: question.items ? question.items.length : 0,
              actualItems: question.items,
              requirement: 'Items array with minimum 2 items required'
            });
            return false;
          }
          
          // Initialize correctOrder if it doesn't exist or isn't an array
          if (!question.correctOrder || !Array.isArray(question.correctOrder)) {
            question.correctOrder = [];
            console.warn(`⚠️ CHRONOLOGICAL ORDER INITIALIZATION - Question ${index + 1}: missing correctOrder array, initializing as empty`, {
              originalCorrectOrder: question.correctOrder,
              newCorrectOrder: [],
              impact: 'Question will be unscorable until correct order is defined'
            });
          }
          
          // Allow empty correctOrder (no correct order defined) but warn about it
          if (question.correctOrder.length === 0) {
            console.warn(`⚠️ CHRONOLOGICAL ORDER WARNING - Question ${index + 1}: no correct order defined - will be unscorable`, {
              correctOrder: question.correctOrder,
              itemsCount: question.items.length,
              recommendation: 'Define correctOrder array to make question scorable'
            });
          }
          
          // Validate that any existing correctOrder indices are within items range
          if (question.correctOrder.length > 0) {
            const invalidIndices = question.correctOrder.filter(idx => 
              typeof idx !== 'number' || idx < 0 || idx >= question.items.length
            );
            
            console.log(`🔍 CHRONOLOGICAL ORDER INDEX VALIDATION - Question ${index + 1}:`, {
              correctOrder: question.correctOrder,
              itemsLength: question.items.length,
              validIndices: question.correctOrder.filter(idx => 
                typeof idx === 'number' && idx >= 0 && idx < question.items.length
              ),
              invalidIndices: invalidIndices,
              indexValidation: question.correctOrder.map(idx => ({
                index: idx,
                isNumber: typeof idx === 'number',
                isValid: typeof idx === 'number' && idx >= 0 && idx < question.items.length,
                itemText: (typeof idx === 'number' && idx >= 0 && idx < question.items.length) 
                  ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text || 'NO TEXT')
                  : 'INVALID INDEX'
              }))
            });
            
            if (invalidIndices.length > 0) {
              console.error(`❌ CHRONOLOGICAL ORDER INDEX VALIDATION FAILED - Question ${index + 1}: invalid correctOrder indices`, {
                invalidIndices: invalidIndices,
                correctOrder: question.correctOrder,
                itemsLength: question.items.length,
                requirement: `All indices must be numbers between 0 and ${question.items.length - 1}`
              });
              return false;
            }
          }
          
          console.log(`✅ CHRONOLOGICAL ORDER VALIDATION PASSED - Question ${index + 1}:`, {
            itemsCount: question.items.length,
            correctOrderCount: question.correctOrder.length,
            isScoreable: question.correctOrder.length > 0,
            validationStatus: 'PASSED'
          });
        } else if (question.type === 'short-answer' || question.type === 'long-form-answer') {
          // Text questions don't need additional validation
        } else {
          console.warn(`❌ Question ${index + 1} FAILED: unsupported type: ${question.type}`);
          return false;
        }
        
        console.log(`✅ Question ${index + 1} PASSED validation`);
        return true;
      });
      
      console.log('Question validation results:', {
        originalCount: foundQuiz.questions.length,
        validatedCount: validatedQuestions.length,
        filteredOut: foundQuiz.questions.length - validatedQuestions.length
      });
      
      if (validatedQuestions.length === 0) {
        console.error('All questions filtered out during validation!', {
          originalQuestions: foundQuiz.questions,
          validationResults: foundQuiz.questions.map((q, i) => {
            const result = {};
            if (!q || typeof q !== 'object') result.reason = 'Not an object';
            else if (!q.type) result.reason = 'Missing type';
            else if (q.type === 'select-all-that-apply') {
              if (!q.options || !Array.isArray(q.options) || q.options.length < 2) {
                result.reason = 'Invalid options array';
              } else if (!q.correctAnswers || !Array.isArray(q.correctAnswers)) {
                result.reason = 'Missing correctAnswers array (should be initialized)';
              }
            }
            return { index: i, question: q, result };
          })
        });
        throw new Error('No valid questions found after validation');
      }
      
      if (validatedQuestions.length < foundQuiz.questions.length) {
        console.warn(`Filtered out ${foundQuiz.questions.length - validatedQuestions.length} invalid questions`);
        foundQuiz = {
          ...foundQuiz,
          questions: validatedQuestions
        };
      }

      setLesson(foundLesson);
      
      // Handle target question count if specified
      if (foundQuiz.targetQuestionCount && foundQuiz.targetQuestionCount > 0 && foundQuiz.questions.length > foundQuiz.targetQuestionCount) {
        // If we have more questions than target, take the first targetQuestionCount questions
        // This prevents array access issues if targetQuestionCount is set incorrectly
        foundQuiz = {
          ...foundQuiz,
          questions: foundQuiz.questions.slice(0, foundQuiz.targetQuestionCount)
        };
        console.log(`Quiz filtered to ${foundQuiz.targetQuestionCount} questions (was ${foundQuiz.questions.length})`);
      }
      
      setQuiz(foundQuiz);
      
      // Initialize timer if quiz has time limit
      if (foundQuiz.timeLimit && foundQuiz.timeLimit > 0) {
        setTimeLeft(foundQuiz.timeLimit * 60); // Convert minutes to seconds
      }

      console.log('Quiz initialized successfully:', {
        questions: foundQuiz.questions.length,
        timeLimit: foundQuiz.timeLimit
      });

      console.log('Quiz state should now be set. Current component states:', {
        quizSet: !!foundQuiz,
        loading: loading,
        error: error,
        quizStarted: quizStarted
      });

    } catch (err) {
      console.error('Error initializing quiz:', err);
      console.error('Quiz initialization error details:', {
        courseId,
        lessonId,
        errorMessage: err.message,
        errorStack: err.stack
      });
      if (isMountedRef.current) {
        setError(err.message);
      }
    } finally {
      if (isMountedRef.current) {
        console.log('Quiz initialization finally block: setting loading to false');
        setLoading(false);
        setInitializing(false);
        console.log('Loading state should now be false, component should re-render');
      } else {
        console.warn('Component unmounted, not setting loading to false');
      }
    }
  }, [courseId, lessonId, getCourseById, initializing]);

  // Submit quiz - MOVED UP to prevent temporal dead zone
  const handleSubmitQuiz = useCallback(async () => {
    if (!isMountedRef.current || submitting || quizCompleted) return;

    try {
      setSubmitting(true);
      console.log('Submitting quiz with answers:', answers);

      // Calculate score
      let correctAnswers = 0;
      let scorableQuestions = 0; // Track questions that can actually be scored

      // Safely iterate through questions
      if (quiz?.questions && Array.isArray(quiz.questions)) {
        for (let i = 0; i < quiz.questions.length; i++) {
          const question = quiz.questions[i];
          if (question && question.id) {
            const userAnswer = answers[question.id];
            
            // Handle different question types  
            if (question.type === 'true-false' && userAnswer === question.correctAnswer) {
              correctAnswers++;
              scorableQuestions++;
            } else if (question.type === 'true-false') {
              scorableQuestions++; // Count as scorable even if incorrect
            } else if (question.type === 'multiple-choice' && userAnswer === question.correctAnswer) {
              correctAnswers++;
              scorableQuestions++;
            } else if (question.type === 'multiple-choice') {
              scorableQuestions++; // Count as scorable even if incorrect
            } else if (question.type === 'select-all-that-apply') {
              // For select-all questions, user must select ALL correct answers and NO incorrect ones
              const userSelectedAnswers = Array.isArray(userAnswer) ? userAnswer : [];
              const correctAnswers_array = Array.isArray(question.correctAnswers) ? question.correctAnswers : [];
              
              // Handle case where no correct answers are defined (unscorable question)
              if (correctAnswers_array.length === 0) {
                console.warn(`Question with ID ${question.id} has no correct answers defined - skipping scoring`);
                // Skip scoring for this question, don't count it in scorableQuestions
                continue;
              }
              
              // Count this as a scorable question
              scorableQuestions++;
              
              // Sort both arrays to compare them properly
              const sortedUserAnswers = [...userSelectedAnswers].sort((a, b) => a - b);
              const sortedCorrectAnswers = [...correctAnswers_array].sort((a, b) => a - b);
              
              // Check if arrays are exactly equal (same length and same elements)
              const isCorrect = sortedUserAnswers.length === sortedCorrectAnswers.length &&
                               sortedUserAnswers.every((answer, index) => answer === sortedCorrectAnswers[index]);
              
              if (isCorrect) {
                correctAnswers++;
              }
            } else if (question.type === 'chronological-order') {
              console.log(`🔍 CHRONOLOGICAL ORDER SCORING - Question ${question.id}:`, {
                questionText: question.question,
                itemsCount: question.items ? question.items.length : 0,
                items: question.items ? question.items.map((item, idx) => ({
                  index: idx,
                  text: typeof item === 'string' ? item : (item?.text || 'NO TEXT')
                })) : 'NO ITEMS'
              });
              
              // For chronological order questions, user must arrange items in the exact correct order
              const userOrder = Array.isArray(userAnswer) ? userAnswer : [];
              const correctOrder = Array.isArray(question.correctOrder) ? question.correctOrder : [];
              
              console.log(`🔍 CHRONOLOGICAL ORDER USER ANSWER - Question ${question.id}:`, {
                userAnswerType: typeof userAnswer,
                userAnswerIsArray: Array.isArray(userAnswer),
                userOrder: userOrder,
                userOrderLength: userOrder.length,
                userOrderSequence: userOrder.map(idx => ({
                  position: userOrder.indexOf(idx) + 1,
                  itemIndex: idx,
                  itemText: (question.items && question.items[idx]) 
                    ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text || 'NO TEXT')
                    : 'INVALID INDEX'
                }))
              });
              
              console.log(`🔍 CHRONOLOGICAL ORDER CORRECT ANSWER - Question ${question.id}:`, {
                correctOrder: correctOrder,
                correctOrderLength: correctOrder.length,
                correctOrderSequence: correctOrder.map(idx => ({
                  position: correctOrder.indexOf(idx) + 1,
                  itemIndex: idx,
                  itemText: (question.items && question.items[idx]) 
                    ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text || 'NO TEXT')
                    : 'INVALID INDEX'
                }))
              });
              
              // Handle case where no correct order is defined (unscorable question)
              if (correctOrder.length === 0) {
                console.warn(`⚠️ CHRONOLOGICAL ORDER SKIP SCORING - Question ${question.id}: no correct order defined`, {
                  correctOrder: correctOrder,
                  userOrder: userOrder,
                  reason: 'Question has no correct order defined - skipping scoring',
                  impact: 'Question will not count toward total score'
                });
                // Skip scoring for this question, don't count it in scorableQuestions
                continue;
              }
              
              // Count this as a scorable question
              scorableQuestions++;
              console.log(`📊 CHRONOLOGICAL ORDER SCORABLE - Question ${question.id}: counting as scorable question`, {
                scorableQuestions: scorableQuestions,
                totalQuestionsProcessed: i + 1
              });
              
              // Check if user order exactly matches correct order (same length and same sequence)
              const lengthMatches = userOrder.length === correctOrder.length;
              const sequenceMatches = lengthMatches && userOrder.every((itemIndex, position) => itemIndex === correctOrder[position]);
              
              console.log(`🔍 CHRONOLOGICAL ORDER COMPARISON - Question ${question.id}:`, {
                lengthMatches: lengthMatches,
                userOrderLength: userOrder.length,
                correctOrderLength: correctOrder.length,
                sequenceMatches: sequenceMatches,
                detailedComparison: userOrder.map((userIdx, pos) => ({
                  position: pos + 1,
                  userItemIndex: userIdx,
                  correctItemIndex: correctOrder[pos],
                  matches: userIdx === correctOrder[pos],
                  userItemText: (question.items && question.items[userIdx]) 
                    ? (typeof question.items[userIdx] === 'string' ? question.items[userIdx] : question.items[userIdx]?.text || 'NO TEXT')
                    : 'INVALID/MISSING',
                  correctItemText: (question.items && question.items[correctOrder[pos]]) 
                    ? (typeof question.items[correctOrder[pos]] === 'string' ? question.items[correctOrder[pos]] : question.items[correctOrder[pos]]?.text || 'NO TEXT')
                    : 'INVALID/MISSING'
                }))
              });
              
              const isCorrect = lengthMatches && sequenceMatches;
              
              if (isCorrect) {
                correctAnswers++;
                console.log(`✅ CHRONOLOGICAL ORDER CORRECT - Question ${question.id}:`, {
                  isCorrect: true,
                  correctAnswers: correctAnswers,
                  scorableQuestions: scorableQuestions,
                  userSequence: userOrder.map(idx => question.items[idx] ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text) : 'INVALID').join(' → '),
                  correctSequence: correctOrder.map(idx => question.items[idx] ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text) : 'INVALID').join(' → ')
                });
              } else {
                console.log(`❌ CHRONOLOGICAL ORDER INCORRECT - Question ${question.id}:`, {
                  isCorrect: false,
                  correctAnswers: correctAnswers,
                  scorableQuestions: scorableQuestions,
                  userSequence: userOrder.map(idx => question.items[idx] ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text) : 'INVALID').join(' → '),
                  correctSequence: correctOrder.map(idx => question.items[idx] ? (typeof question.items[idx] === 'string' ? question.items[idx] : question.items[idx]?.text) : 'INVALID').join(' → '),
                  failureReason: !lengthMatches ? 'Length mismatch' : 'Sequence mismatch'
                });
              }
            } else if (question.type === 'short-answer' || question.type === 'long-form-answer') {
              // For text answers, basic string comparison (case-insensitive)
              scorableQuestions++;
              const correctAnswer = question.correctAnswer || '';
              const userAnswerText = (userAnswer || '').toString().trim().toLowerCase();
              const correctAnswerText = correctAnswer.toString().trim().toLowerCase();
              if (userAnswerText === correctAnswerText) {
                correctAnswers++;
              }
            }
          }
        }
      }

      // Use scorableQuestions instead of total questions for score calculation
      const totalQuestions = scorableQuestions;

      const score = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
      const passed = score >= (quiz?.passingScore || 70);

      // Update progress
      if (updateEnrollmentProgress && typeof updateEnrollmentProgress === 'function') {
        const progressResult = await updateEnrollmentProgress(courseId, {
          progress: passed ? 100 : 0, // Set progress to 100% if passed, 0% if failed
          currentLessonId: lessonId,
          timeSpent: quiz?.timeLimit ? (quiz.timeLimit * 60 - (timeLeft || 0)) : null
        });

        if (progressResult.success) {
          if (isMountedRef.current) {
            setQuizCompleted(true);
            
            toast({
              title: passed ? "🎉 Quiz Passed!" : "📝 Quiz Completed",
              description: `Your score: ${score}% ${passed ? '(Passed)' : '(Below passing score)'}`,
              duration: 3000,
            });

            // Navigate to course after delay
            setTimeout(() => {
              if (isMountedRef.current) {
                navigate(`/course/${courseId}`);
              }
            }, 2000);
          }
        } else {
          throw new Error('Failed to update progress');
        }
      } else {
        throw new Error('updateEnrollmentProgress function not available');
      }

    } catch (err) {
      console.error('Error submitting quiz:', err);
      if (isMountedRef.current) {
        toast({
          title: "Error submitting quiz",
          description: "Please try again or contact support if the problem persists.",
          variant: "destructive",
        });
      }
    } finally {
      if (isMountedRef.current) {
        setSubmitting(false);
      }
    }
  }, [answers, quiz, courseId, lessonId, timeLeft, submitting, quizCompleted, updateEnrollmentProgress, toast, navigate]);

  // Initialize quiz on mount
  useEffect(() => {
    initializeQuiz();
  }, [initializeQuiz]);

  // Timer management with proper cleanup
  useEffect(() => {
    // Clear any existing timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Start timer if conditions are met
    if (quizStarted && timeLeft !== null && timeLeft > 0 && !quizCompleted && quiz?.questions) {
      timerRef.current = setInterval(() => {
        if (!isMountedRef.current) return;
        
        setTimeLeft(prev => {
          if (prev <= 1) {
            return 0; // Will trigger auto-submit via separate effect
          }
          return prev - 1;
        });
      }, 1000);
    }

    // Cleanup function
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [quizStarted, timeLeft, quizCompleted, quiz]);

  // Auto-submit when time runs out
  useEffect(() => {
    if (quizStarted && timeLeft === 0 && !quizCompleted && !submitting && isMountedRef.current) {
      console.log('Time up - auto-submitting quiz');
      handleSubmitQuiz();
    }
  }, [timeLeft, quizStarted, quizCompleted, submitting, handleSubmitQuiz]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Format time display
  const formatTime = (seconds) => {
    if (seconds === null) return '';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Start quiz
  const handleStartQuiz = useCallback(() => {
    if (!isMountedRef.current) return;
    setQuizStarted(true);
    console.log('Quiz started');
  }, []);

  // Handle answer change
  const handleAnswerChange = useCallback((questionId, answer) => {
    if (!isMountedRef.current) return;
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  }, []);

  // Navigate between questions
  const handlePreviousQuestion = useCallback(() => {
    if (!isMountedRef.current || !quiz?.questions) return;
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => Math.max(0, prev - 1));
    }
  }, [currentQuestionIndex, quiz]);

  const handleNextQuestion = useCallback(() => {
    if (!isMountedRef.current || !quiz?.questions) return;
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => Math.min(quiz.questions.length - 1, prev + 1));
    }
  }, [currentQuestionIndex, quiz]);



  // Add render state logging
  console.log('QuizTakingNewFixed render - Component states:', {
    loading,
    error,
    quizStarted,
    hasQuiz: !!quiz,
    quizQuestionsLength: quiz?.questions?.length
  });

  // Loading state
  if (loading) {
    console.log('Rendering loading state');
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading quiz...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error state
  if (error) {
    console.log('Rendering error state:', error);
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Loading Error</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="space-y-2">
              <Button 
                onClick={() => navigate(`/course/${courseId}`)}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Course
              </Button>
              <Button 
                onClick={() => window.location.reload()}
                variant="outline"
                className="w-full"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Quiz not started state
  if (!quizStarted) {
    console.log('Rendering quiz not started state');
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="mb-6">
            <Button 
              onClick={() => navigate(`/course/${courseId}`)}
              variant="outline"
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </div>

          <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                <span>{lesson?.title || 'Quiz'}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span>Questions: {quiz?.questions?.length || 0}</span>
                  </div>
                  {quiz?.timeLimit && (
                    <div className="flex items-center space-x-2">
                      <Timer className="w-4 h-4 text-orange-600" />
                      <span>Time Limit: {quiz.timeLimit} minutes</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-blue-600" />
                    <span>Passing Score: {quiz?.passingScore || 70}%</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-purple-600" />
                    <span>Max Attempts: {quiz?.maxAttempts || 'Unlimited'}</span>
                  </div>
                </div>

                {quiz?.description && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 text-sm">{quiz.description}</p>
                  </div>
                )}

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-800 mb-2">Instructions:</h4>
                  <ul className="text-yellow-700 text-sm space-y-1">
                    <li>• Read each question carefully before answering</li>
                    <li>• You can navigate between questions using the Next/Previous buttons</li>
                    <li>• Make sure to answer all questions before submitting</li>
                    {quiz?.timeLimit && <li>• The quiz will auto-submit when time runs out</li>}
                    <li>• Click "Submit Quiz" when you're ready to finish</li>
                  </ul>
                </div>
              </div>

              <Button 
                onClick={handleStartQuiz}
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
              >
                Start Quiz
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Quiz completed state
  if (quizCompleted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Submitted!</h3>
            <p className="text-gray-600 mb-4">Returning to course...</p>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Main quiz taking interface
  // Add comprehensive null checks to prevent React Error #31
  if (!quiz || !quiz.questions || !Array.isArray(quiz.questions) || quiz.questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz Error</h3>
            <p className="text-gray-600 mb-4">Quiz data is invalid or missing questions</p>
            <Button onClick={() => navigate(`/course/${courseId}`)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Ensure currentQuestionIndex is within bounds
  const safeCurrentQuestionIndex = Math.max(0, Math.min(currentQuestionIndex, quiz.questions.length - 1));
  const rawCurrentQuestion = quiz.questions[safeCurrentQuestionIndex];
  
  // Create a safely validated current question object
  const currentQuestion = rawCurrentQuestion && typeof rawCurrentQuestion === 'object' ? {
    ...rawCurrentQuestion,
    id: rawCurrentQuestion.id || `question-${safeCurrentQuestionIndex}`,
    type: rawCurrentQuestion.type || 'unknown',
    text: rawCurrentQuestion.text || '',
    options: Array.isArray(rawCurrentQuestion.options) ? rawCurrentQuestion.options : [],
    items: Array.isArray(rawCurrentQuestion.items) ? rawCurrentQuestion.items : []
  } : null;
  
  // Additional safety check for currentQuestion
  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Question Error</h3>
            <p className="text-gray-600 mb-4">Current question could not be loaded</p>
            <Button onClick={() => navigate(`/course/${courseId}`)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Course
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const progress = ((safeCurrentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <Button 
            onClick={() => navigate(`/course/${courseId}`)}
            variant="outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Course
          </Button>
          
          {timeLeft !== null && (
            <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg border">
              <Timer className="w-4 h-4 text-orange-600" />
              <span className="font-mono text-lg font-semibold">
                {formatTime(timeLeft)}
              </span>
            </div>
          )}
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Question {safeCurrentQuestionIndex + 1} of {quiz.questions.length}
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">
              {currentQuestion?.question || 'Question not available'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* True/False Questions */}
            {currentQuestion?.type === 'true-false' && (
              <div className="space-y-3">
                {[true, false].map((value) => (
                  <label
                    key={`tf-${value.toString()}`}
                    className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestion.id || 'unknown'}`}
                      value={value.toString()}
                      checked={answers[currentQuestion.id] === value}
                      onChange={(e) => {
                        if (currentQuestion?.id) {
                          handleAnswerChange(currentQuestion.id, e.target.value === 'true');
                        }
                      }}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="flex-1">{value ? 'True' : 'False'}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Multiple Choice Questions */}
            {currentQuestion?.type === 'multiple-choice' && (
              <div className="space-y-3">
                {(Array.isArray(currentQuestion.options) ? currentQuestion.options : []).map((option, index) => {
                  // Handle both string and object option formats with defensive programming
                  const optionText = typeof option === 'string' ? option : (option?.text || `Option ${index + 1}`);
                  const optionImage = typeof option === 'object' ? option?.image : null;
                  const optionAudio = typeof option === 'object' ? option?.audio : null;
                  
                  return (
                    <label
                      key={`mc-${index}`}
                      className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="radio"
                        name={`question-${currentQuestion.id || 'unknown'}`}
                        value={index.toString()}
                        checked={answers[currentQuestion.id] === index}
                        onChange={(e) => {
                          if (currentQuestion?.id) {
                            handleAnswerChange(currentQuestion.id, parseInt(e.target.value));
                          }
                        }}
                        className="w-4 h-4 text-blue-600 mt-1"
                      />
                      <div className="flex-1">
                        <span className="block text-gray-900">{optionText}</span>
                        
                        {/* Display option image if available */}
                        {optionImage && optionImage.trim() !== '' && (
                          <div className="mt-2">
                            <img 
                              src={optionImage} 
                              alt={`Option ${index + 1}`} 
                              className="max-w-xs h-32 object-cover rounded border"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                        
                        {/* Display option audio if available */}
                        {optionAudio && optionAudio.trim() !== '' && (
                          <div className="mt-2">
                            <audio controls className="w-full max-w-xs">
                              <source src={optionAudio} type="audio/mpeg" />
                              Your browser does not support the audio element.
                            </audio>
                          </div>
                        )}
                      </div>
                    </label>
                  );
                })}
                
                {/* Fallback if no options available */}
                {(!currentQuestion.options || !Array.isArray(currentQuestion.options) || currentQuestion.options.length === 0) && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">No answer options available for this question.</p>
                  </div>
                )}
              </div>
            )}

            {/* Select All That Apply Questions */}
            {currentQuestion?.type === 'select-all-that-apply' && (
              <div className="space-y-3">
                {(Array.isArray(currentQuestion.options) ? currentQuestion.options : []).map((option, index) => {
                  // Handle both string and object option formats with defensive programming
                  const optionText = typeof option === 'string' ? option : (option?.text || `Option ${index + 1}`);
                  const optionImage = typeof option === 'object' ? option?.image : null;
                  const optionAudio = typeof option === 'object' ? option?.audio : null;
                  
                  // Get current selected answers (array of indices)
                  const selectedAnswers = Array.isArray(answers[currentQuestion.id]) ? answers[currentQuestion.id] : [];
                  const isSelected = selectedAnswers.includes(index);
                  
                  return (
                    <label
                      key={`sata-${index}`}
                      className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="checkbox"
                        name={`question-${currentQuestion.id || 'unknown'}`}
                        value={index.toString()}
                        checked={isSelected}
                        onChange={(e) => {
                          if (currentQuestion?.id) {
                            const currentAnswers = Array.isArray(answers[currentQuestion.id]) ? answers[currentQuestion.id] : [];
                            let newAnswers;
                            
                            if (e.target.checked) {
                              // Add this index to selected answers
                              newAnswers = [...currentAnswers, index];
                            } else {
                              // Remove this index from selected answers
                              newAnswers = currentAnswers.filter(idx => idx !== index);
                            }
                            
                            handleAnswerChange(currentQuestion.id, newAnswers);
                          }
                        }}
                        className="w-4 h-4 text-blue-600 mt-1"
                      />
                      <div className="flex-1">
                        <span className="block text-gray-900">{optionText}</span>
                        
                        {/* Display option image if available */}
                        {optionImage && optionImage.trim() !== '' && (
                          <div className="mt-2">
                            <img 
                              src={optionImage} 
                              alt={`Option ${index + 1}`} 
                              className="max-w-xs h-32 object-cover rounded border"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                        
                        {/* Display option audio if available */}
                        {optionAudio && optionAudio.trim() !== '' && (
                          <div className="mt-2">
                            <audio controls className="w-full max-w-xs">
                              <source src={optionAudio} type="audio/mpeg" />
                              Your browser does not support the audio element.
                            </audio>
                          </div>
                        )}
                      </div>
                    </label>
                  );
                })}
                
                {/* Fallback if no options available */}
                {(!currentQuestion.options || !Array.isArray(currentQuestion.options) || currentQuestion.options.length === 0) && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">No answer options available for this question.</p>
                  </div>
                )}
                
                {/* Show selected count */}
                {Array.isArray(answers[currentQuestion.id]) && answers[currentQuestion.id].length > 0 && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-blue-800 text-sm">
                      ✓ Selected {answers[currentQuestion.id].length} option{answers[currentQuestion.id].length !== 1 ? 's' : ''}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Chronological Order Questions */}  
            {currentQuestion?.type === 'chronological-order' && (
              <div className="space-y-4">
                {(() => {
                  console.log(`🔍 CHRONOLOGICAL ORDER RENDERING - Question ${currentQuestion.id}:`, {
                    questionText: currentQuestion.question,
                    hasItems: !!(currentQuestion.items),
                    isItemsArray: Array.isArray(currentQuestion.items),
                    itemsLength: currentQuestion.items ? currentQuestion.items.length : 0,
                    itemsContent: currentQuestion.items ? currentQuestion.items.map((item, idx) => ({
                      index: idx,
                      type: typeof item,
                      text: typeof item === 'string' ? item : (item?.text || 'NO TEXT'),
                      hasImage: !!(typeof item === 'object' && item?.image),
                      hasAudio: !!(typeof item === 'object' && item?.audio)
                    })) : 'NO ITEMS',
                    currentAnswer: answers[currentQuestion.id],
                    currentAnswerType: typeof answers[currentQuestion.id],
                    currentAnswerIsArray: Array.isArray(answers[currentQuestion.id])
                  });
                  return null;
                })()}
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <p className="text-blue-800 text-sm">
                    📋 <strong>Instructions:</strong> Click items in the correct chronological order to arrange them.
                  </p>
                </div>
                
                {/* Display items for ordering */}
                {(Array.isArray(currentQuestion.items) ? currentQuestion.items : []).map((item, index) => {
                  // Handle both string and object item formats with defensive programming
                  const itemText = typeof item === 'string' ? item : (item?.text || `Item ${index + 1}`);
                  const itemImage = typeof item === 'object' ? item?.image : null;
                  const itemAudio = typeof item === 'object' ? item?.audio : null;
                  
                  // Get current order (array of indices representing the user's arrangement)
                  const currentOrder = Array.isArray(answers[currentQuestion.id]) ? answers[currentQuestion.id] : [];
                  const itemPosition = currentOrder.indexOf(index);
                  const isOrdered = itemPosition !== -1;
                  
                  console.log(`🔍 CHRONOLOGICAL ORDER ITEM RENDER - Item ${index}:`, {
                    itemIndex: index,
                    itemText: itemText,
                    itemType: typeof item,
                    hasImage: !!itemImage,
                    hasAudio: !!itemAudio,
                    currentOrder: currentOrder,
                    itemPosition: itemPosition,
                    isOrdered: isOrdered,
                    currentAnswer: answers[currentQuestion.id]
                  });
                  
                  return (
                    <div
                      key={`co-${index}`}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        isOrdered 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                      onClick={() => {
                        console.log(`🔍 CHRONOLOGICAL ORDER ITEM CLICK - Item ${index}:`, {
                          itemIndex: index,
                          itemText: itemText,
                          currentOrder: currentOrder,
                          isOrdered: isOrdered,
                          questionId: currentQuestion.id
                        });
                        
                        if (currentQuestion?.id) {
                          const currentOrder = Array.isArray(answers[currentQuestion.id]) ? [...answers[currentQuestion.id]] : [];
                          
                          if (isOrdered) {
                            // Remove from order
                            const newOrder = currentOrder.filter(idx => idx !== index);
                            console.log(`🔄 CHRONOLOGICAL ORDER REMOVE - Item ${index}:`, {
                              oldOrder: currentOrder,
                              newOrder: newOrder,
                              removedItem: itemText,
                              action: 'REMOVE'
                            });
                            handleAnswerChange(currentQuestion.id, newOrder);
                          } else {
                            // Add to end of order
                            const newOrder = [...currentOrder, index];
                            console.log(`🔄 CHRONOLOGICAL ORDER ADD - Item ${index}:`, {
                              oldOrder: currentOrder,
                              newOrder: newOrder,
                              addedItem: itemText,
                              newPosition: newOrder.length,
                              action: 'ADD'
                            });
                            handleAnswerChange(currentQuestion.id, newOrder);
                          }
                        }
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="text-sm font-medium text-gray-600">Item {index + 1}</span>
                            {isOrdered && (
                              <span className="px-2 py-1 bg-blue-500 text-white text-xs rounded-full">
                                Position: {itemPosition + 1}
                              </span>
                            )}
                          </div>
                          <p className="text-gray-900 font-medium">{itemText}</p>
                          
                          {/* Display item image if available */}
                          {itemImage && itemImage.trim() !== '' && (
                            <div className="mt-2">
                              <img 
                                src={itemImage} 
                                alt={`Item ${index + 1}`} 
                                className="max-w-xs h-32 object-cover rounded border"
                                onError={(e) => {
                                  console.warn(`🖼️ CHRONOLOGICAL ORDER IMAGE ERROR - Item ${index}:`, {
                                    itemIndex: index,
                                    imageUrl: itemImage,
                                    error: 'Failed to load image'
                                  });
                                  e.target.style.display = 'none';
                                }}
                                onLoad={() => {
                                  console.log(`🖼️ CHRONOLOGICAL ORDER IMAGE LOADED - Item ${index}:`, {
                                    itemIndex: index,
                                    imageUrl: itemImage
                                  });
                                }}
                              />
                            </div>
                          )}
                          
                          {/* Display item audio if available */}
                          {itemAudio && itemAudio.trim() !== '' && (
                            <div className="mt-2">
                              <audio 
                                controls 
                                className="w-full max-w-xs"
                                onError={() => {
                                  console.warn(`🔊 CHRONOLOGICAL ORDER AUDIO ERROR - Item ${index}:`, {
                                    itemIndex: index,
                                    audioUrl: itemAudio,
                                    error: 'Failed to load audio'
                                  });
                                }}
                                onCanPlay={() => {
                                  console.log(`🔊 CHRONOLOGICAL ORDER AUDIO LOADED - Item ${index}:`, {
                                    itemIndex: index,
                                    audioUrl: itemAudio
                                  });
                                }}
                              >
                                <source src={itemAudio} type="audio/mpeg" />
                                Your browser does not support the audio element.
                              </audio>
                            </div>
                          )}
                        </div>
                        
                        <div className="ml-4">
                          {isOrdered ? (
                            <div className="text-blue-600">
                              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            </div>
                          ) : (
                            <div className="text-gray-400">
                              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {/* Fallback if no items available */}
                {(!currentQuestion.items || !Array.isArray(currentQuestion.items) || currentQuestion.items.length === 0) && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">No items available for ordering in this question.</p>
                    {(() => {
                      console.error(`❌ CHRONOLOGICAL ORDER NO ITEMS - Question ${currentQuestion.id}:`, {
                        items: currentQuestion.items,
                        hasItems: !!(currentQuestion.items),
                        isArray: Array.isArray(currentQuestion.items),
                        length: currentQuestion.items ? currentQuestion.items.length : 0
                      });
                      return null;
                    })()}
                  </div>
                )}
                
                {/* Show current order */}
                {Array.isArray(answers[currentQuestion.id]) && answers[currentQuestion.id].length > 0 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    {(() => {
                      const currentOrder = answers[currentQuestion.id];
                      console.log(`📝 CHRONOLOGICAL ORDER CURRENT ORDER DISPLAY - Question ${currentQuestion.id}:`, {
                        currentOrder: currentOrder,
                        orderLength: currentOrder.length,
                        itemsInOrder: currentOrder.map(itemIndex => ({
                          position: currentOrder.indexOf(itemIndex) + 1,
                          itemIndex: itemIndex,
                          itemText: currentQuestion.items[itemIndex] 
                            ? (typeof currentQuestion.items[itemIndex] === 'string' 
                                ? currentQuestion.items[itemIndex] 
                                : currentQuestion.items[itemIndex]?.text || 'NO TEXT')
                            : 'INVALID INDEX'
                        }))
                      });
                      return null;
                    })()}
                    
                    <p className="text-green-800 text-sm font-medium mb-1">
                      📝 Your Current Order:
                    </p>
                    <p className="text-green-700 text-sm">
                      {answers[currentQuestion.id].map((itemIndex, position) => {
                        const item = currentQuestion.items[itemIndex];
                        const itemText = typeof item === 'string' ? item : (item?.text || `Item ${itemIndex + 1}`);
                        return `${position + 1}. ${itemText}`;
                      }).join(' → ')}
                    </p>
                  </div>
                )}
                
                {/* Instructions for reordering */}
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    💡 <strong>Tip:</strong> Click items in the order you think they should be arranged chronologically. Click again to remove from your order.
                  </p>
                </div>
              </div>
            )}

            {/* Short Answer Questions */}
            {currentQuestion?.type === 'short-answer' && (
              <Textarea
                placeholder="Enter your answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => {
                  if (currentQuestion?.id) {
                    handleAnswerChange(currentQuestion.id, e.target.value);
                  }
                }}
                className="min-h-[100px]"
              />
            )}

            {/* Long Form Answer Questions */}
            {currentQuestion?.type === 'long-form-answer' && (
              <Textarea
                placeholder="Enter your detailed answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => {
                  if (currentQuestion?.id) {
                    handleAnswerChange(currentQuestion.id, e.target.value);
                  }
                }}
                className="min-h-[200px]"
              />
            )}



            {/* Fallback for unknown question types */}
            {currentQuestion && !['true-false', 'multiple-choice', 'select-all-that-apply', 'chronological-order', 'short-answer', 'long-form-answer'].includes(currentQuestion.type) && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800">
                  Unsupported question type: {currentQuestion.type}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation and Submit */}
        <div className="flex items-center justify-between">
          <Button
            onClick={handlePreviousQuestion}
            disabled={safeCurrentQuestionIndex === 0}
            variant="outline"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="flex space-x-3">
            {safeCurrentQuestionIndex < quiz.questions.length - 1 ? (
              <Button onClick={handleNextQuestion}>
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizTakingNewFixed;