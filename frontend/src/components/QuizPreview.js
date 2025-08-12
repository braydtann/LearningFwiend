import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Checkbox } from './ui/checkbox';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import ScreenRecorder from './ScreenRecorder';
import { 
  X, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  HelpCircle,
  CheckCircle,
  Target,
  FileImage,
  Video,
  Mic
} from 'lucide-react';

const QuizPreview = ({ isOpen, onClose, quizData }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  if (!quizData || !quizData.questions) return null;

  const currentQuestion = quizData.questions[currentQuestionIndex];
  const hasNextQuestion = currentQuestionIndex < (quizData.questions.length - 1);
  const hasPrevQuestion = currentQuestionIndex > 0;

  const handleAnswerChange = (questionIndex, value) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: value
    }));
  };

  const nextQuestion = () => {
    if (hasNextQuestion) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (hasPrevQuestion) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const renderQuestionContent = () => {
    if (!currentQuestion) return <div className="text-center py-8 text-gray-500">No question content</div>;

    const questionKey = currentQuestionIndex;
    const userAnswer = selectedAnswers[questionKey];

    return (
      <div className="space-y-6">
        {/* Question Header */}
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Question {currentQuestionIndex + 1}
              </h3>
              <p className="text-gray-700 leading-relaxed">{currentQuestion.text}</p>
            </div>
            <div className="ml-4 flex flex-col items-end space-y-2">
              <Badge variant="outline" className="flex items-center">
                <Target className="w-3 h-3 mr-1" />
                {currentQuestion.points || 1} pts
              </Badge>
              {currentQuestion.timeLimit && (
                <Badge variant="secondary" className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {currentQuestion.timeLimit}s
                </Badge>
              )}
            </div>
          </div>

          {/* Media Content */}
          {currentQuestion.media && (
            <div className="bg-gray-50 rounded-lg p-4">
              {currentQuestion.media.type === 'image' && (
                <div className="flex items-center text-gray-600">
                  <FileImage className="w-5 h-5 mr-2" />
                  <span className="text-sm">Image: {currentQuestion.media.url}</span>
                </div>
              )}
              {currentQuestion.media.type === 'video' && (
                <div className="flex items-center text-gray-600">
                  <Video className="w-5 h-5 mr-2" />
                  <span className="text-sm">Video: {currentQuestion.media.url}</span>
                </div>
              )}
              {currentQuestion.media.type === 'audio' && (
                <div className="flex items-center text-gray-600">
                  <Mic className="w-5 h-5 mr-2" />
                  <span className="text-sm">Audio: {currentQuestion.media.url}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Answer Options */}
        <div className="space-y-4">
          {renderAnswerOptions(currentQuestion, questionKey, userAnswer)}
        </div>

        {/* Question Type Badge */}
        <div className="pt-4 border-t">
          <Badge variant="outline" className="text-xs">
            {getQuestionTypeLabel(currentQuestion.type)}
          </Badge>
        </div>
      </div>
    );
  };

  const renderAnswerOptions = (question, questionKey, userAnswer) => {
    switch (question.type) {
      case 'multiple_choice':
        return (
          <RadioGroup 
            value={userAnswer || ''} 
            onValueChange={(value) => handleAnswerChange(questionKey, value)}
          >
            <div className="space-y-3">
              {question.options?.map((option, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`q${questionKey}_${index}`} />
                  <Label htmlFor={`q${questionKey}_${index}`} className="flex-1 cursor-pointer">
                    {option}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        );

      case 'select_all':
        return (
          <div className="space-y-3">
            {question.options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <Checkbox 
                  id={`q${questionKey}_${index}`}
                  checked={Array.isArray(userAnswer) && userAnswer.includes(option)}
                  onCheckedChange={(checked) => {
                    const currentAnswers = Array.isArray(userAnswer) ? userAnswer : [];
                    if (checked) {
                      handleAnswerChange(questionKey, [...currentAnswers, option]);
                    } else {
                      handleAnswerChange(questionKey, currentAnswers.filter(a => a !== option));
                    }
                  }}
                />
                <Label htmlFor={`q${questionKey}_${index}`} className="flex-1 cursor-pointer">
                  {option}
                </Label>
              </div>
            ))}
          </div>
        );

      case 'true_false':
        return (
          <RadioGroup 
            value={userAnswer || ''} 
            onValueChange={(value) => handleAnswerChange(questionKey, value)}
          >
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="true" id={`q${questionKey}_true`} />
                <Label htmlFor={`q${questionKey}_true`} className="cursor-pointer">True</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="false" id={`q${questionKey}_false`} />
                <Label htmlFor={`q${questionKey}_false`} className="cursor-pointer">False</Label>
              </div>
            </div>
          </RadioGroup>
        );

      case 'short_answer':
        return (
          <Input
            placeholder="Type your short answer here..."
            value={userAnswer || ''}
            onChange={(e) => handleAnswerChange(questionKey, e.target.value)}
            className="w-full"
          />
        );

      case 'long_form':
        return (
          <Textarea
            placeholder="Type your detailed answer here..."
            rows={6}
            value={userAnswer || ''}
            onChange={(e) => handleAnswerChange(questionKey, e.target.value)}
            className="w-full"
          />
        );

      case 'chronological_order':
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-600 mb-3">
              Drag items to arrange them in chronological order (preview mode - drag disabled):
            </p>
            <div className="space-y-2">
              {question.items?.map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg border cursor-move">
                  <span className="text-sm font-medium text-gray-700">
                    {index + 1}. {item}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'record_screen':
      case 'record-screen':
        return (
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Video className="w-8 h-8 text-red-600" />
              </div>
              <h4 className="font-medium text-red-900 mb-2">Screen Recording Question</h4>
              <p className="text-sm text-red-700 mb-4">
                Students will be able to record their screen to demonstrate their knowledge
              </p>
              <Button variant="outline" size="sm" disabled>
                Start Recording (Preview Mode)
              </Button>
            </div>
            {question.instructions && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 className="font-medium text-blue-900 mb-2">Instructions:</h5>
                <p className="text-sm text-blue-800">{question.instructions}</p>
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-400">
            <HelpCircle className="w-16 h-16 mx-auto mb-4" />
            <p>Unknown question type: {question.type}</p>
          </div>
        );
    }
  };

  const getQuestionTypeLabel = (type) => {
    const labels = {
      'multiple_choice': 'Multiple Choice',
      'select_all': 'Select All That Apply',
      'true_false': 'True/False',
      'short_answer': 'Short Answer',
      'long_form': 'Long Form Answer',
      'chronological_order': 'Chronological Order',
      'record_screen': 'Screen Recording',
      'record-screen': 'Screen Recording'
    };
    return labels[type] || type;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl">{quizData.title} - Preview</DialogTitle>
              <div className="flex items-center space-x-4 mt-2">
                <Badge variant="secondary" className="flex items-center">
                  <HelpCircle className="w-3 h-3 mr-1" />
                  {quizData.questions.length} questions
                </Badge>
                {quizData.timeLimit && (
                  <Badge variant="outline" className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {quizData.timeLimit} minutes
                  </Badge>
                )}
                {quizData.passingScore && (
                  <Badge variant="outline" className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {quizData.passingScore}% to pass
                  </Badge>
                )}
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden" style={{ height: 'calc(90vh - 120px)' }}>
          {/* Question Navigation Sidebar */}
          <div className="lg:col-span-1 bg-gray-50 rounded-lg p-4 overflow-y-auto">
            <h3 className="font-semibold text-gray-900 mb-4">Questions</h3>
            <div className="space-y-2">
              {quizData.questions.map((question, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    index === currentQuestionIndex 
                      ? 'bg-blue-100 text-blue-900 border border-blue-200' 
                      : 'hover:bg-white'
                  }`}
                  onClick={() => setCurrentQuestionIndex(index)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">Q{index + 1}</span>
                    {selectedAnswers[index] && (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    )}
                  </div>
                  <div className="text-xs text-gray-600 mt-1 truncate">
                    {question.text}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Question Area */}
          <div className="lg:col-span-3 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto">
              <Card>
                <CardContent className="p-6">
                  {renderQuestionContent()}
                </CardContent>
              </Card>
            </div>

            {/* Navigation Controls */}
            <div className="flex items-center justify-between pt-4 border-t">
              <Button
                variant="outline"
                onClick={prevQuestion}
                disabled={!hasPrevQuestion}
                className="flex items-center"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>

              <div className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {quizData.questions.length}
              </div>

              <Button
                variant="outline"
                onClick={nextQuestion}
                disabled={!hasNextQuestion}
                className="flex items-center"
              >
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default QuizPreview;