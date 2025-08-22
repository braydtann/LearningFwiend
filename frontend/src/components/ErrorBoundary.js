import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { Button } from './ui/button';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: 0 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Check if this is React Error #310
    const isReactError310 = error.message && (
      error.message.includes('Cannot read') ||
      error.message.includes('undefined') ||
      error.stack?.includes('at QuizTaking')
    );

    this.setState({
      error,
      errorInfo,
      isReactError310
    });

    // Optional: Log to error reporting service
    if (window.reportError) {
      window.reportError(error, {
        component: 'ErrorBoundary',
        errorInfo,
        retryCount: this.state.retryCount
      });
    }
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      const { error, isReactError310, retryCount } = this.state;
      
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Oops! Something went wrong
            </h1>
            
            {isReactError310 ? (
              <div className="mb-6">
                <p className="text-gray-600 mb-3">
                  The quiz encountered a technical issue. This usually happens when 
                  navigating quickly between quiz questions or when the quiz data is loading.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                  <p className="text-sm text-blue-800">
                    <strong>What you can do:</strong>
                  </p>
                  <ul className="text-sm text-blue-700 mt-2 space-y-1 text-left">
                    <li>• Try refreshing the page</li>
                    <li>• Go back to the course and try again</li>
                    <li>• Clear your browser cache if the problem persists</li>
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-gray-600 mb-6">
                An unexpected error occurred. Please try refreshing the page or 
                contact support if the problem continues.
              </p>
            )}

            <div className="space-y-3">
              {retryCount < 3 ? (
                <Button 
                  onClick={this.handleRetry}
                  className="w-full"
                  variant="default"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again {retryCount > 0 && `(${retryCount + 1}/3)`}
                </Button>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                  <p className="text-sm text-yellow-800">
                    Multiple retry attempts failed. Please refresh the page manually 
                    or contact support.
                  </p>
                </div>
              )}
              
              <Button 
                onClick={this.handleGoHome}
                variant="outline"
                className="w-full"
              >
                <Home className="w-4 h-4 mr-2" />
                Go to Dashboard
              </Button>
            </div>

            {process.env.NODE_ENV === 'development' && error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                  Technical Details (Development Only)
                </summary>
                <div className="mt-2 bg-gray-100 rounded-lg p-3 text-xs font-mono text-gray-700 overflow-auto max-h-40">
                  <strong>Error:</strong> {error.toString()}
                  <br />
                  <strong>Stack:</strong>
                  <pre className="mt-1 whitespace-pre-wrap">{error.stack}</pre>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;