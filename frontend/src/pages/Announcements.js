import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { mockAnnouncements, mockCourses } from '../data/mockData';
import { MessageSquare, Calendar, BookOpen, Plus } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../hooks/use-toast';

const Announcements = () => {
  const { user, isLearner } = useAuth();
  const { toast } = useToast();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newAnnouncement, setNewAnnouncement] = useState({
    title: '',
    message: '',
    courseId: ''
  });

  const handleCreateAnnouncement = () => {
    if (!newAnnouncement.title || !newAnnouncement.message) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required information.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Announcement created!",
      description: "Your announcement has been posted successfully.",
    });

    setNewAnnouncement({ title: '', message: '', courseId: '' });
    setIsCreateModalOpen(false);
  };

  const getAnnouncementsForUser = () => {
    if (isLearner) {
      // For learners, show announcements from their enrolled courses
      return mockAnnouncements;
    } else {
      // For instructors/admins, show all announcements or their own
      return mockAnnouncements;
    }
  };

  const announcements = getAnnouncementsForUser();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Announcements</h1>
          <p className="text-gray-600">
            {isLearner 
              ? 'Stay updated with course announcements and news'
              : 'Communicate with your students and manage announcements'
            }
          </p>
        </div>
        
        {!isLearner && (
          <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                New Announcement
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Create Announcement</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    placeholder="Enter announcement title"
                    value={newAnnouncement.title}
                    onChange={(e) => setNewAnnouncement(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="courseId">Course (Optional)</Label>
                  <Select 
                    value={newAnnouncement.courseId} 
                    onValueChange={(value) => setNewAnnouncement(prev => ({ ...prev, courseId: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select course or leave blank for general" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">General Announcement</SelectItem>
                      {mockCourses.map(course => (
                        <SelectItem key={course.id} value={course.id}>
                          {course.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="message">Message</Label>
                  <Textarea
                    id="message"
                    placeholder="Enter your announcement message"
                    rows={4}
                    value={newAnnouncement.message}
                    onChange={(e) => setNewAnnouncement(prev => ({ ...prev, message: e.target.value }))}
                  />
                </div>
                
                <div className="flex items-center justify-end space-x-3 pt-4">
                  <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateAnnouncement}>
                    Post Announcement
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Announcements</p>
                <p className="text-2xl font-bold text-blue-700">{announcements.length}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">This Week</p>
                <p className="text-2xl font-bold text-green-700">2</p>
              </div>
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Course Specific</p>
                <p className="text-2xl font-bold text-orange-700">
                  {announcements.filter(a => a.courseId).length}
                </p>
              </div>
              <BookOpen className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Announcements List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Recent Announcements</CardTitle>
        </CardHeader>
        <CardContent>
          {announcements.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No announcements yet</h3>
              <p className="text-gray-600">
                {isLearner 
                  ? 'Check back later for updates from your instructors'
                  : 'Create your first announcement to communicate with students'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {announcements.map((announcement) => {
                const course = mockCourses.find(c => c.id === announcement.courseId);
                
                return (
                  <Card key={announcement.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {announcement.title}
                            </h3>
                            {course && (
                              <Badge variant="secondary">
                                {course.title}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center text-sm text-gray-600 mb-3">
                            <span>by {announcement.author}</span>
                            <span className="mx-2">•</span>
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              {new Date(announcement.createdAt).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700 leading-relaxed">
                          {announcement.message}
                        </p>
                      </div>
                      
                      {course && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="flex items-center space-x-3">
                            <img 
                              src={course.thumbnail} 
                              alt={course.title}
                              className="w-10 h-10 rounded-lg object-cover"
                            />
                            <div>
                              <p className="font-medium text-gray-900">{course.title}</p>
                              <p className="text-sm text-gray-600">{course.category}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Announcements;