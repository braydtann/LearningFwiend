import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { getUserCertificates } from '../data/mockData';
import { Award, Download, Share2, Calendar } from 'lucide-react';

const Certificates = () => {
  const { user } = useAuth();
  const certificates = getUserCertificates(user?.id);

  const handleDownload = (certificateId) => {
    // Mock download functionality
    console.log(`Downloading certificate ${certificateId}`);
  };

  const handleShare = (certificateId) => {
    // Mock share functionality
    console.log(`Sharing certificate ${certificateId}`);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Certificates</h1>
        <p className="text-gray-600">Your earned certificates and achievements</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Total Certificates</p>
                <p className="text-2xl font-bold text-green-700">{certificates.length}</p>
              </div>
              <Award className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Courses Completed</p>
                <p className="text-2xl font-bold text-blue-700">{certificates.length}</p>
              </div>
              <Award className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Achievement Points</p>
                <p className="text-2xl font-bold text-purple-700">{certificates.length * 100}</p>
              </div>
              <Award className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Certificates Grid */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Earned Certificates</CardTitle>
        </CardHeader>
        <CardContent>
          {certificates.length === 0 ? (
            <div className="text-center py-12">
              <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No certificates yet</h3>
              <p className="text-gray-600 mb-4">Complete courses to earn your first certificate</p>
              <Button onClick={() => window.location.href = '/courses'}>
                Browse Courses
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {certificates.map((certificate) => (
                <Card key={certificate.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    {/* Certificate Visual */}
                    <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg p-6 text-white mb-4">
                      <div className="text-center">
                        <Award className="h-12 w-12 mx-auto mb-3" />
                        <h3 className="text-lg font-bold mb-2">Certificate of Completion</h3>
                        <div className="border-t border-white/20 pt-3">
                          <p className="text-sm opacity-90">{certificate.courseName}</p>
                        </div>
                      </div>
                    </div>

                    {/* Certificate Details */}
                    <div className="space-y-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{certificate.courseName}</h4>
                        <div className="flex items-center text-sm text-gray-600 mt-1">
                          <Calendar className="w-4 h-4 mr-1" />
                          Issued {new Date(certificate.issuedAt).toLocaleDateString()}
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-800">
                          Verified
                        </Badge>
                        <Badge variant="outline">
                          Certificate ID: {certificate.id}
                        </Badge>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2 pt-3">
                        <Button 
                          size="sm" 
                          className="flex-1"
                          onClick={() => handleDownload(certificate.id)}
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleShare(certificate.id)}
                        >
                          <Share2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Certificate Preview Modal would go here in a real implementation */}
    </div>
  );
};

export default Certificates;