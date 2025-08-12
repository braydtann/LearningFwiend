import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import PasswordChangeModal from './PasswordChangeModal';
import { useToast } from '../hooks/use-toast';

const ProtectedRoute = ({ children }) => {
  const { user, loading, requiresPasswordChange } = useAuth();
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);
  const { toast } = useToast();

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Show password change modal if required
  if (requiresPasswordChange) {
    return (
      <>
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Password Change Required</h2>
            <p className="text-gray-600 mb-4">
              You must change your temporary password before accessing the system.
            </p>
          </div>
        </div>
        <PasswordChangeModal
          isOpen={true}
          onClose={() => {}} // Prevent closing - password change is required
          onSuccess={() => {
            toast({
              title: "Password updated!",
              description: "Your password has been successfully changed.",
            });
            // The auth context will update and remove the requiresPasswordChange flag
          }}
          currentUser={user}
        />
      </>
    );
  }

  // Render the protected content
  return children;
};

export default ProtectedRoute;