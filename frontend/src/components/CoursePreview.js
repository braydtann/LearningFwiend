import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { 
  X, 
  Play, 
  FileText, 
  Link, 
  Download, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  BookOpen
} from 'lucide-react';

const CoursePreview = ({ isOpen, onClose, courseData }) => {
  const [currentModuleIndex, setCurrentModuleIndex] = useState(0);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);

  if (!courseData || !courseData.modules) return null;

  const currentModule = courseData.modules[currentModuleIndex];
  const currentLesson = currentModule?.lessons?.[currentLessonIndex];
  const hasNextLesson = currentLessonIndex < (currentModule?.lessons?.length - 1);
  const hasPrevLesson = currentLessonIndex > 0;
  const hasNextModule = currentModuleIndex < (courseData.modules.length - 1);
  const hasPrevModule = currentModuleIndex > 0;

  const nextLesson = () => {
    if (hasNextLesson) {
      setCurrentLessonIndex(prev => prev + 1);
    } else if (hasNextModule) {
      setCurrentModuleIndex(prev => prev + 1);
      setCurrentLessonIndex(0);
    }
  };

  const prevLesson = () => {
    if (hasPrevLesson) {
      setCurrentLessonIndex(prev => prev - 1);
    } else if (hasPrevModule) {
      setCurrentModuleIndex(prev => prev - 1);
      const prevModule = courseData.modules[currentModuleIndex - 1];
      setCurrentLessonIndex(prevModule.lessons.length - 1);
    }
  };

  const renderLessonContent = () => {
    if (!currentLesson) return <div className="text-center py-8 text-gray-500">No lesson content</div>;

    switch (currentLesson.type) {
      case 'video':
        return (
          <div className="space-y-4">
            <div className="bg-black rounded-lg aspect-video flex items-center justify-center">
              {currentLesson.videoUrl ? (
                <div className="text-center text-white">
                  <Play className="w-16 h-16 mx-auto mb-4" />
                  <p className="text-sm opacity-75">Video: {currentLesson.videoUrl}</p>
                  <p className="text-xs opacity-50 mt-2">Click to play in actual course</p>
                </div>
              ) : (
                <div className="text-center text-gray-400">
                  <Play className="w-16 h-16 mx-auto mb-4" />
                  <p>No video URL provided</p>
                </div>
              )}
            </div>
            {currentLesson.duration && (
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                Duration: {currentLesson.duration}
              </div>
            )}
          </div>
        );

      case 'canva':
        return (
          <div className="space-y-4">
            {currentLesson.embedCode ? (
              <div className="border rounded-lg aspect-video overflow-hidden">
                <div 
                  className="w-full h-full"
                  dangerouslySetInnerHTML={{ __html: currentLesson.embedCode }}
                />
              </div>
            ) : currentLesson.canvaUrl ? (
              <div className="bg-gray-100 rounded-lg aspect-video flex items-center justify-center">
                <div className="text-center">
                  <Link className="w-16 h-16 mx-auto mb-4 text-blue-600" />
                  <p className="text-sm text-gray-600">Canva Presentation</p>
                  <p className="text-xs text-blue-600 mt-2">{currentLesson.canvaUrl}</p>
                  <p className="text-xs text-gray-400 mt-2">Opens in new tab in actual course</p>
                </div>
              </div>
            ) : (
              <div className="bg-gray-100 rounded-lg aspect-video flex items-center justify-center">
                <div className="text-center text-gray-400">
                  <Link className="w-16 h-16 mx-auto mb-4" />
                  <p>No Canva content provided</p>
                </div>
              </div>
            )}
          </div>
        );

      case 'text':
        return (
          <div className="space-y-4">
            <div className="prose max-w-none">
              {currentLesson.content ? (
                <div className="whitespace-pre-wrap text-gray-700">
                  {currentLesson.content}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FileText className="w-16 h-16 mx-auto mb-4" />
                  <p>No text content provided</p>
                </div>
              )}
            </div>
            
            {currentLesson.attachments && currentLesson.attachments.length > 0 && (
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Download className="w-4 h-4 mr-2" />
                  Attachments ({currentLesson.attachments.length})
                </h4>
                <div className="space-y-2">
                  {currentLesson.attachments.map((attachment, index) => (
                    <div key={index} className="flex items-center p-2 bg-gray-50 rounded-lg">
                      <FileText className="w-4 h-4 text-blue-600 mr-2" />
                      <span className="text-sm font-medium">{attachment.name}</span>
                      <Badge variant="secondary" className="ml-auto text-xs">
                        {attachment.type}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'pdf':
        return (
          <div className="space-y-4">
            <div className="bg-red-50 rounded-lg aspect-video flex items-center justify-center border-2 border-red-200">
              <div className="text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-red-600" />
                <p className="text-sm text-red-700">PDF Document</p>
                {currentLesson.content && (
                  <p className="text-xs text-red-600 mt-2">{currentLesson.content}</p>
                )}
                <p className="text-xs text-gray-400 mt-2">PDF viewer in actual course</p>
              </div>
            </div>
          </div>
        );

      case 'google_drive':
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 rounded-lg aspect-video flex items-center justify-center border-2 border-blue-200">
              <div className="text-center">
                <Link className="w-16 h-16 mx-auto mb-4 text-blue-600" />
                <p className="text-sm text-blue-700">Google Drive Content</p>
                {currentLesson.content && (
                  <p className="text-xs text-blue-600 mt-2">{currentLesson.content}</p>
                )}
                <p className="text-xs text-gray-400 mt-2">Google Drive embed in actual course</p>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-400">
            <FileText className="w-16 h-16 mx-auto mb-4" />
            <p>Unknown lesson type: {currentLesson.type}</p>
          </div>
        );
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl">{courseData.title} - Preview</DialogTitle>
              <div className="flex items-center space-x-4 mt-2">
                <Badge variant="secondary">{courseData.category}</Badge>
                <Badge variant="outline" className="flex items-center">
                  <BookOpen className="w-3 h-3 mr-1" />
                  {courseData.modules.length} modules
                </Badge>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden" style={{ height: 'calc(90vh - 120px)' }}>
          {/* Course Navigation Sidebar */}
          <div className="lg:col-span-1 bg-gray-50 rounded-lg p-4 overflow-y-auto">
            <h3 className="font-semibold text-gray-900 mb-4">Course Contents</h3>
            <div className="space-y-2">
              {courseData.modules.map((module, moduleIndex) => (
                <div key={moduleIndex} className="space-y-1">
                  <div className={`p-2 rounded-lg cursor-pointer transition-colors ${
                    moduleIndex === currentModuleIndex ? 'bg-blue-100 text-blue-900' : 'hover:bg-white'
                  }`}>
                    <div className="font-medium text-sm">
                      Module {moduleIndex + 1}: {module.title || `Module ${moduleIndex + 1}`}
                    </div>
                  </div>
                  
                  {module.lessons.map((lesson, lessonIndex) => (
                    <div
                      key={lessonIndex}
                      className={`ml-4 p-2 rounded-lg cursor-pointer transition-colors text-sm ${
                        moduleIndex === currentModuleIndex && lessonIndex === currentLessonIndex
                          ? 'bg-blue-200 text-blue-900 font-medium'
                          : 'text-gray-600 hover:bg-white'
                      }`}
                      onClick={() => {
                        setCurrentModuleIndex(moduleIndex);
                        setCurrentLessonIndex(lessonIndex);
                      }}
                    >
                      {lesson.title || `Lesson ${lessonIndex + 1}`}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3 flex flex-col overflow-hidden">
            <div className="border-b pb-4 mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {currentLesson?.title || `Lesson ${currentLessonIndex + 1}`}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Module {currentModuleIndex + 1} of {courseData.modules.length} • 
                Lesson {currentLessonIndex + 1} of {currentModule?.lessons?.length || 0}
              </p>
            </div>

            <div className="flex-1 overflow-y-auto">
              <Card>
                <CardContent className="p-6">
                  {renderLessonContent()}
                </CardContent>
              </Card>
            </div>

            {/* Navigation Controls */}
            <div className="flex items-center justify-between pt-4 border-t">
              <Button
                variant="outline"
                onClick={prevLesson}
                disabled={!hasPrevLesson && !hasPrevModule}
                className="flex items-center"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>

              <div className="text-sm text-gray-600">
                {currentModuleIndex + 1}.{currentLessonIndex + 1}
              </div>

              <Button
                variant="outline"
                onClick={nextLesson}
                disabled={!hasNextLesson && !hasNextModule}
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

export default CoursePreview;