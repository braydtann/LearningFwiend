import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Shield, ArrowRight, Clock } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';
import { loginPalService } from '../../services/loginPalService';

const LoginPalButton = ({ className = '', disabled = false }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleClick = async () => {
    setIsLoading(true);
    
    try {
      // Simulate checking LoginPal status
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "LoginPal Integration Coming Soon",
        description: "LoginPal OAuth service is being deployed. Once ready, you'll be able to sign in with unified role and permission management.",
        variant: "default",
      });
      
      // In the future, this will initiate actual OAuth flow:
      // window.location.href = await initiateLoginPalOAuth();
      
    } catch (error) {
      toast({
        title: "Service Unavailable",
        description: "LoginPal authentication service is not yet available.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <Button
        type="button"
        variant="outline"
        className="w-full h-12 border-2 border-indigo-200 hover:border-indigo-300 hover:bg-indigo-50 text-indigo-700 font-medium relative group transition-all duration-300"
        onClick={handleClick}
        disabled={disabled || isLoading}
      >
        <div className="flex items-center justify-center space-x-3">
          {isLoading ? (
            <>
              <div className="w-6 h-6 flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
              <span>Checking LoginPal...</span>
            </>
          ) : (
            <>
              <div className="w-6 h-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-sm">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <span>Continue with LoginPal</span>
              <ArrowRight className="w-4 h-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" />
            </>
          )}
        </div>
        
        {/* Hover effect overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
      </Button>
      
      {/* Status indicator */}
      <div className="absolute -top-1 -right-1 flex items-center">
        <div className="w-3 h-3 bg-orange-400 rounded-full flex items-center justify-center">
          <Clock className="w-2 h-2 text-white" />
        </div>
      </div>
      
      {/* Tooltip-style info */}
      <div className="mt-2 text-xs text-center text-gray-500">
        <span className="inline-flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>OAuth integration pending deployment</span>
        </span>
      </div>
    </div>
  );
};

export default LoginPalButton;