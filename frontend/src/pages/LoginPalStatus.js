import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Shield, Clock, CheckCircle, AlertCircle, Settings, Webhook, Users } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { loginPalService } from '../services/loginPalService';

const LoginPalStatus = () => {
  const [status, setStatus] = useState(null);
  const [users, setUsers] = useState([]);
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statusData, usersData, webhooksData] = await Promise.all([
        loginPalService.checkStatus(),
        loginPalService.getUsers(),
        loginPalService.getWebhooks()
      ]);

      setStatus(statusData);
      setUsers(usersData.users || []);
      setWebhooks(webhooksData.webhooks || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load LoginPal status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const testOAuthFlow = async () => {
    try {
      const result = await loginPalService.initiateOAuth();
      toast({
        title: "OAuth Test",
        description: result.message,
        variant: result.status === "placeholder" ? "default" : "success",
      });
    } catch (error) {
      toast({
        title: "OAuth Test Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">LoginPal Integration Status</h1>
          <p className="text-gray-600">Monitor OAuth service and user synchronization</p>
        </div>
        <Button onClick={loadData} variant="outline">
          Refresh
        </Button>
      </div>

      {/* Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Service Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                <Clock className="w-4 h-4 text-orange-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Service Status</p>
                <Badge variant={status?.ready ? "success" : "secondary"}>
                  {status?.ready ? "Ready" : "Pending Deployment"}
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Synced Users</p>
                <p className="text-lg font-semibold">{users.length}</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Webhook className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Webhook Events</p>
                <p className="text-lg font-semibold">{webhooks.length}</p>
              </div>
            </div>
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Integration Status</h4>
                <p className="text-sm text-blue-800 mt-1">{status?.message}</p>
                {status?.endpoints && (
                  <div className="mt-2">
                    <p className="text-xs text-blue-700 mb-1">Available Endpoints:</p>
                    <div className="grid grid-cols-2 gap-1 text-xs">
                      {Object.entries(status.endpoints).map(([key, endpoint]) => (
                        <code key={key} className="bg-blue-100 px-1 py-0.5 rounded text-blue-800">
                          {endpoint}
                        </code>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Test OAuth Button */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5" />
            <span>Testing & Configuration</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Button onClick={testOAuthFlow} className="mr-3">
                Test OAuth Flow
              </Button>
              <span className="text-sm text-gray-600">
                Test the LoginPal OAuth initiation (will show placeholder response)
              </span>
            </div>
            
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-medium mb-2">When LoginPal is ready:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Configure OAuth application in LoginPal dashboard</li>
                <li>• Update environment variables with client credentials</li>
                <li>• Set webhook URL for user sync events</li>
                <li>• Replace placeholder endpoints with real OAuth implementation</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      {users.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Synced Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Name</th>
                    <th className="text-left p-2">Email</th>
                    <th className="text-left p-2">Role</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-left p-2">Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b">
                      <td className="p-2">{user.name || 'N/A'}</td>
                      <td className="p-2">{user.email}</td>
                      <td className="p-2">
                        <Badge variant={user.role === 'admin' ? 'destructive' : user.role === 'instructor' ? 'default' : 'secondary'}>
                          {user.role}
                        </Badge>
                      </td>
                      <td className="p-2">
                        {user.verified_email ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-orange-600" />
                        )}
                      </td>
                      <td className="p-2">{new Date(user.updated_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Webhooks Log */}
      {webhooks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Webhook Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {webhooks.slice(0, 10).map((webhook, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">{webhook.event_type}</Badge>
                      <span className="text-sm">User: {webhook.user_id}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(webhook.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default LoginPalStatus;