import React from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Plus, Trash2, ArrowUp, ArrowDown } from 'lucide-react';

const FinalTestQuestionInterface = ({ 
  question, 
  questionIndex, 
  onQuestionChange, 
  onOptionChange, 
  onOptionMediaChange,
  onItemChange,
  onRemoveQuestion,
  onAddOption,
  onRemoveOption,
  onAddItem,
  onRemoveItem,
  onMoveItemUp,
  onMoveItemDown
}) => {
  return (
    <Card key={question.id} className="border-purple-200 bg-purple-50/30">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <Badge variant="outline" className="border-purple-300 text-purple-700">
            Question {questionIndex + 1}
          </Badge>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => onRemoveQuestion(questionIndex)}
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>

        <div className="space-y-4">
          {/* Question Type and Points */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <Label className="text-sm">Question Type</Label>
              <Select 
                value={question.type || 'multiple_choice'} 
                onValueChange={(value) => onQuestionChange(questionIndex, 'type', value)}
              >
                <SelectTrigger className="border-purple-300 focus:border-purple-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="multiple_choice">Multiple Choice</SelectItem>
                  <SelectItem value="select-all-that-apply">Select All That Apply</SelectItem>
                  <SelectItem value="true_false">True/False</SelectItem>
                  <SelectItem value="short_answer">Short Answer</SelectItem>
                  <SelectItem value="essay">Long Form Answer</SelectItem>
                  <SelectItem value="chronological-order">Chronological Order</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-sm">Points</Label>
              <Input
                type="number"
                placeholder="10"
                min="1"
                value={question.points}
                onChange={(e) => onQuestionChange(questionIndex, 'points', parseInt(e.target.value) || 10)}
              />
            </div>
          </div>

          {/* Question Text */}
          <div className="space-y-2">
            <Label className="text-sm">Question Text</Label>
            <Textarea
              placeholder="Enter your comprehensive question here..."
              rows={3}
              value={question.question}
              onChange={(e) => onQuestionChange(questionIndex, 'question', e.target.value)}
              className="border-purple-300 focus:border-purple-500"
            />
          </div>

          {/* Question Media */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label className="text-sm">Question Image URL (Optional)</Label>
              <Input
                placeholder="https://example.com/image.jpg"
                value={question.questionImage || ''}
                onChange={(e) => onQuestionChange(questionIndex, 'questionImage', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label className="text-sm">Question Audio URL (Optional)</Label>
              <Input
                placeholder="https://example.com/audio.mp3"
                value={question.questionAudio || ''}
                onChange={(e) => onQuestionChange(questionIndex, 'questionAudio', e.target.value)}
              />
            </div>
          </div>

          {/* Media Preview */}
          {question.questionImage && (
            <div className="mt-2">
              <img src={question.questionImage} alt="Question" className="max-w-xs h-32 object-cover rounded border" />
            </div>
          )}
          {question.questionAudio && (
            <div className="mt-2">
              <audio controls className="w-full max-w-xs">
                <source src={question.questionAudio} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}

          {/* Multiple Choice Questions */}
          {(question.type === 'multiple_choice' || !question.type) && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-sm">Answer Options</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onAddOption(questionIndex)}
                  className="border-purple-300 text-purple-700 hover:bg-purple-50"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Option
                </Button>
              </div>
              {(question.options || []).map((option, optionIndex) => (
                <div key={optionIndex} className="border border-purple-200 rounded-lg p-3 space-y-3 bg-purple-50/50">
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name={`final-correct-${question.id}`}
                      checked={String(question.correctAnswer) === String(optionIndex)}
                      onChange={() => {
                        console.log('🔴 RADIO BUTTON CLICKED:', {
                          questionIndex,
                          optionIndex,
                          questionId: question.id,
                          currentCorrectAnswer: question.correctAnswer
                        });
                        onQuestionChange(questionIndex, 'correctAnswer', optionIndex);
                      }}
                      className="text-purple-600"
                    />
                    <Input
                      placeholder={`Option ${optionIndex + 1} text`}
                      value={option || ''}
                      onChange={(e) => onOptionChange(questionIndex, optionIndex, e.target.value)}
                    />
                    {(question.options || []).length > 2 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => onRemoveOption(questionIndex, optionIndex)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Select All That Apply Questions */}
          {question.type === 'select-all-that-apply' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-sm">Answer Options (Select all correct answers)</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onAddOption(questionIndex)}
                  className="border-purple-300 text-purple-700 hover:bg-purple-50"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Option
                </Button>
              </div>
              {(question.options || []).map((option, optionIndex) => (
                <div key={optionIndex} className="border border-purple-200 rounded-lg p-3 space-y-3 bg-purple-50/50">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={(question.correctAnswers || []).includes(optionIndex)}
                      onChange={(e) => {
                        const currentAnswers = question.correctAnswers || [];
                        const newAnswers = e.target.checked
                          ? [...currentAnswers, optionIndex]
                          : currentAnswers.filter(index => index !== optionIndex);
                        onQuestionChange(questionIndex, 'correctAnswers', newAnswers);
                      }}
                      className="text-purple-600"
                    />
                    <Input
                      placeholder={`Option ${optionIndex + 1} text`}
                      value={option || ''}
                      onChange={(e) => onOptionChange(questionIndex, optionIndex, e.target.value)}
                    />
                    {(question.options || []).length > 2 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => onRemoveOption(questionIndex, optionIndex)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                  
                  {/* Option Media - Same as above */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-6">
                    <div className="space-y-1">
                      <Label className="text-xs">Option Image URL</Label>
                      <Input
                        placeholder="https://example.com/option-image.jpg"
                        value={option?.image || ''}
                        onChange={(e) => onOptionMediaChange(questionIndex, optionIndex, 'image', e.target.value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Option Audio URL</Label>
                      <Input
                        placeholder="https://example.com/option-audio.mp3"
                        value={option?.audio || ''}
                        onChange={(e) => onOptionMediaChange(questionIndex, optionIndex, 'audio', e.target.value)}
                      />
                    </div>
                  </div>
                  
                  {/* Media Preview */}
                  {option?.image && (
                    <div className="ml-6">
                      <img src={option.image} alt={`Option ${optionIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                    </div>
                  )}
                  {option?.audio && (
                    <div className="ml-6">
                      <audio controls className="w-full max-w-xs">
                        <source src={option.audio} type="audio/mpeg" />
                      </audio>
                    </div>
                  )}
                </div>
              ))}
              <p className="text-xs text-purple-600">Check the boxes next to all correct answers. Students must select ALL correct options to get points.</p>
            </div>
          )}

          {/* True/False Questions */}
          {question.type === 'true_false' && (
            <div className="space-y-2">
              <Label className="text-sm">Correct Answer</Label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name={`true_false-${question.id}`}
                    checked={String(question.correctAnswer) === 'true'}
                    onChange={() => onQuestionChange(questionIndex, 'correctAnswer', 'true')}
                    className="text-purple-600"
                  />
                  <span>True</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name={`true_false-${question.id}`}
                    checked={String(question.correctAnswer) === 'false'}
                    onChange={() => onQuestionChange(questionIndex, 'correctAnswer', 'false')}
                    className="text-purple-600"
                  />
                  <span>False</span>
                </label>
              </div>
            </div>
          )}

          {/* Short Answer Questions */}
          {question.type === 'short_answer' && (
            <div className="space-y-2">
              <Label className="text-sm">Sample Answer (for instructor reference)</Label>
              <Input
                placeholder="Provide a sample short answer"
                value={question.sampleAnswer || ''}
                onChange={(e) => onQuestionChange(questionIndex, 'sampleAnswer', e.target.value)}
              />
              <p className="text-xs text-purple-600">Short answers require manual grading by the instructor.</p>
            </div>
          )}

          {/* Long Form Answer Questions */}
          {question.type === 'essay' && (
            <div className="space-y-2">
              <Label className="text-sm">Sample Answer (for instructor reference)</Label>
              <Textarea
                placeholder="Provide a sample answer to guide manual grading"
                rows={4}
                value={question.sampleAnswer || ''}
                onChange={(e) => onQuestionChange(questionIndex, 'sampleAnswer', e.target.value)}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm">Word Limit (optional)</Label>
                  <Input
                    type="number"
                    placeholder="500"
                    value={question.wordLimit || ''}
                    onChange={(e) => onQuestionChange(questionIndex, 'wordLimit', parseInt(e.target.value) || null)}
                  />
                </div>
              </div>
              <p className="text-xs text-purple-600">Long form answers require manual grading by the instructor.</p>
            </div>
          )}

          {/* Chronological Order Questions */}
          {question.type === 'chronological-order' && (
            <div className="space-y-3">
              <Label className="text-sm">Items to Order (Use arrows to set correct chronological sequence)</Label>
              {(question.items || []).map((item, itemIndex) => (
                <div key={itemIndex} className="border border-purple-200 rounded-lg p-3 space-y-3 bg-purple-50/50">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-purple-700 min-w-[80px]">Position {itemIndex + 1}:</span>
                    <Input
                      placeholder={`Item ${itemIndex + 1} text`}
                      value={item || ''}
                      onChange={(e) => onItemChange(questionIndex, itemIndex, e.target.value)}
                    />
                    <div className="flex items-center space-x-1">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => onMoveItemUp && onMoveItemUp(questionIndex, itemIndex)}
                        disabled={itemIndex === 0}
                        className="text-blue-600 hover:text-blue-700"
                        title="Move item up"
                      >
                        <ArrowUp className="w-4 h-4" />
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => onMoveItemDown && onMoveItemDown(questionIndex, itemIndex)}
                        disabled={itemIndex === (question.items || []).length - 1}
                        className="text-blue-600 hover:text-blue-700"
                        title="Move item down"
                      >
                        <ArrowDown className="w-4 h-4" />
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => onRemoveItem(questionIndex, itemIndex)}
                        disabled={(question.items || []).length <= 2}
                        className="text-red-600 hover:text-red-700"
                        title="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => onAddItem(questionIndex)}
                className="border-purple-300 text-purple-700 hover:bg-purple-50"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Item
              </Button>
              <p className="text-xs text-purple-600">Use the arrow buttons to arrange items in the correct chronological order. Students will need to arrange them correctly.</p>
            </div>
          )}

          {/* Explanation for all question types */}
          <div className="space-y-2">
            <Label className="text-sm">Explanation (Optional)</Label>
            <Textarea
              placeholder="Explain why this is the correct answer"
              rows={2}
              value={question.explanation || ''}
              onChange={(e) => onQuestionChange(questionIndex, 'explanation', e.target.value)}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FinalTestQuestionInterface;