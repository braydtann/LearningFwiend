import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Trash2, Database, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const AdminUtilities = () => {
  const { user, isAdmin, cleanupOrphanedEnrollments } = useAuth();
  const { toast } = useToast();
  const [cleaning, setCleaning] = useState(false);
  const [lastCleanupResult, setLastCleanupResult] = useState(null);

  // Redirect non-admins
  if (!isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">Only administrators can access utility functions.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleCleanupOrphanedEnrollments = async () => {
    setCleaning(true);
    setLastCleanupResult(null);

    try {
      const result = await cleanupOrphanedEnrollments();
      setLastCleanupResult(result);

      if (result.success) {
        toast({
          title: "Cleanup Completed",
          description: result.message,
          duration: 5000,
        });
      } else {
        toast({
          title: "Cleanup Failed",
          description: result.error,
          variant: "destructive",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Cleanup error:', error);
      toast({
        title: "Cleanup Error",
        description: "An unexpected error occurred during cleanup.",
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setCleaning(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Utilities</h1>
        <p className="text-gray-600">System maintenance and cleanup tools</p>
      </div>

      {/* Data Cleanup Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-600" />
            <span>Data Cleanup Tools</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Orphaned Enrollments Cleanup */}
          <div className="border rounded-lg p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Orphaned Enrollments Cleanup</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Remove enrollment records that reference deleted courses or classrooms. 
                  This fixes "Unknown Course" entries appearing on student dashboards.
                </p>
                <div className="flex items-center space-x-2 text-xs">
                  <Badge variant="outline">Safe Operation</Badge>
                  <Badge variant="outline">Student Data Preserved</Badge>
                </div>
              </div>
              <Button
                onClick={handleCleanupOrphanedEnrollments}
                disabled={cleaning}
                variant="outline"
                className="flex items-center space-x-2"
              >
                {cleaning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Cleaning...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    <span>Clean Up</span>
                  </>
                )}
              </Button>
            </div>

            {/* Last Cleanup Result */}
            {lastCleanupResult && (
              <div className={`mt-4 p-3 rounded-lg border ${
                lastCleanupResult.success 
                  ? 'bg-green-50 border-green-200' 
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  {lastCleanupResult.success ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  )}
                  <span className={`font-medium ${
                    lastCleanupResult.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {lastCleanupResult.success ? 'Success' : 'Error'}
                  </span>
                </div>
                <p className={`text-sm ${
                  lastCleanupResult.success ? 'text-green-700' : 'text-red-700'
                }`}>
                  {lastCleanupResult.success 
                    ? `${lastCleanupResult.message} (${lastCleanupResult.deletedCount} records cleaned)`
                    : lastCleanupResult.error
                  }
                </p>
              </div>
            )}
          </div>

          {/* Future utility tools can be added here */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="font-semibold text-gray-700 mb-2">Additional Tools</h3>
            <p className="text-sm text-gray-600">
              More system maintenance tools will be available here in future updates.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Instructions Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Usage Instructions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-1">When to use Orphaned Enrollments Cleanup:</h4>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Students report seeing "Unknown Course" entries on their dashboard</li>
                <li>After deleting courses or classrooms in bulk</li>
                <li>During system maintenance or data migration</li>
                <li>When enrollment statistics appear inflated</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-1">What this cleanup does:</h4>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Identifies enrollment records pointing to non-existent courses</li>
                <li>Safely removes these orphaned records from the database</li>
                <li>Preserves all valid enrollment data and student progress</li>
                <li>Updates enrollment counts and statistics</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminUtilities;