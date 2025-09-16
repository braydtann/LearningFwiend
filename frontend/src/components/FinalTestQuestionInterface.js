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
  onRemoveItem
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
                  <SelectItem value="select_all_that_apply">Select All That Apply</SelectItem>
                  <SelectItem value="true_false">True/False</SelectItem>
                  <SelectItem value="short_answer">Short Answer</SelectItem>
                  <SelectItem value="essay">Long Form Answer</SelectItem>
                  <SelectItem value="chronological_order">Chronological Order</SelectItem>
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
                      checked={question.correctAnswer === optionIndex}
                      onChange={() => onQuestionChange(questionIndex, 'correctAnswer', optionIndex)}
                      className="text-purple-600"
                    />
                    <Input
                      placeholder={`Option ${optionIndex + 1} text`}
                      value={option?.text || ''}
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
                  
                  {/* Option Media */}
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
              <p className="text-xs text-purple-600">Select the radio button next to the correct answer. Add images or audio to enhance your options.</p>
            </div>
          )}

          {/* Select All That Apply Questions */}
          {question.type === 'select_all_that_apply' && (
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
                      value={option?.text || ''}
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
                    name={`true-false-${question.id}`}
                    checked={question.correctAnswer === 0}
                    onChange={() => onQuestionChange(questionIndex, 'correctAnswer', 0)}
                    className="text-purple-600"
                  />
                  <span>True</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name={`true-false-${question.id}`}
                    checked={question.correctAnswer === 1}
                    onChange={() => onQuestionChange(questionIndex, 'correctAnswer', 1)}
                    className="text-purple-600"
                  />
                  <span>False</span>
                </label>
              </div>
            </div>
          )}

          {/* Short Answer Questions */}
          {question.type === 'short-answer' && (
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
          {question.type === 'long-form-answer' && (
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
              <Label className="text-sm">Items to Order</Label>
              {(question.items || []).map((item, itemIndex) => (
                <div key={itemIndex} className="border border-purple-200 rounded-lg p-3 space-y-3 bg-purple-50/50">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-purple-700 min-w-[80px]">Position {itemIndex + 1}:</span>
                    <Input
                      placeholder={`Item ${itemIndex + 1} text`}
                      value={item?.text || ''}
                      onChange={(e) => onItemChange(questionIndex, itemIndex, 'text', e.target.value)}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => onRemoveItem(questionIndex, itemIndex)}
                      disabled={(question.items || []).length <= 2}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {/* Item Media */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-20">
                    <div className="space-y-1">
                      <Label className="text-xs">Item Image URL</Label>
                      <Input
                        placeholder="https://example.com/item-image.jpg"
                        value={item?.image || ''}
                        onChange={(e) => onItemChange(questionIndex, itemIndex, 'image', e.target.value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Item Audio URL</Label>
                      <Input
                        placeholder="https://example.com/item-audio.mp3"
                        value={item?.audio || ''}
                        onChange={(e) => onItemChange(questionIndex, itemIndex, 'audio', e.target.value)}
                      />
                    </div>
                  </div>
                  
                  {/* Media Preview */}
                  {item?.image && (
                    <div className="ml-20">
                      <img src={item.image} alt={`Item ${itemIndex + 1}`} className="max-w-xs h-20 object-cover rounded border" />
                    </div>
                  )}
                  {item?.audio && (
                    <div className="ml-20">
                      <audio controls className="w-full max-w-xs">
                        <source src={item.audio} type="audio/mpeg" />
                      </audio>
                    </div>
                  )}
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
              <div className="space-y-2">
                <Label className="text-sm">Correct Order</Label>
                <p className="text-xs text-purple-600 mb-2">
                  Specify the correct chronological order by entering the position numbers (1, 2, 3, etc.)
                </p>
                <Input
                  placeholder="e.g., 2,1,4,3 (comma-separated position numbers)"
                  value={question.correctOrder ? question.correctOrder.map(i => i + 1).join(',') : ''}
                  onChange={(e) => {
                    const order = e.target.value.split(',').map(num => parseInt(num.trim()) - 1).filter(num => !isNaN(num));
                    onQuestionChange(questionIndex, 'correctOrder', order);
                  }}
                />
              </div>
              <p className="text-xs text-purple-600">Students will drag and drop these items into the correct chronological order. Add images or audio to enhance the items.</p>
            </div>
          )}

          {/* Record Screen Questions */}
          {question.type === 'record-screen' && (
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium text-red-900">Screen Recording Question</h4>
                    <p className="text-sm text-red-700">Students will record their screen to demonstrate their knowledge</p>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-red-900">Recording Instructions</Label>
                    <Textarea
                      placeholder="Provide clear instructions for what the student should demonstrate on screen..."
                      rows={3}
                      value={question.instructions || ''}
                      onChange={(e) => onQuestionChange(questionIndex, 'instructions', e.target.value)}
                      className="border-red-300 focus:border-red-500"
                    />
                    <p className="text-xs text-red-600">
                      Be specific about what actions the student should perform and what they should show.
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-red-900">Max Recording Time (minutes)</Label>
                      <Input
                        type="number"
                        placeholder="5"
                        min="1"
                        max="30"
                        value={question.maxRecordingTime || ''}
                        onChange={(e) => onQuestionChange(questionIndex, 'maxRecordingTime', parseInt(e.target.value) || 5)}
                        className="border-red-300 focus:border-red-500"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-red-900">Required Software/Tools</Label>
                      <Input
                        placeholder="e.g., VS Code, Browser, Excel"
                        value={question.requiredTools || ''}
                        onChange={(e) => onQuestionChange(questionIndex, 'requiredTools', e.target.value)}
                        className="border-red-300 focus:border-red-500"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-red-900">Evaluation Criteria</Label>
                    <Textarea
                      placeholder="What criteria will be used to grade this recording? Be specific about what constitutes a good answer..."
                      rows={2}
                      value={question.evaluationCriteria || ''}
                      onChange={(e) => onQuestionChange(questionIndex, 'evaluationCriteria', e.target.value)}
                      className="border-red-300 focus:border-red-500"
                    />
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h5 className="font-medium text-blue-900 mb-2">💡 Tips for Screen Recording Questions:</h5>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Provide step-by-step instructions</li>
                  <li>• Specify the expected outcome or result</li>
                  <li>• Mention any files or resources students need</li>
                  <li>• Set a reasonable time limit for the task</li>
                </ul>
              </div>
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