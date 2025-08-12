import React from 'react';

const Progress = ({ value = 0, className = '', ...props }) => {
  return (
    <div 
      className={`w-full bg-gray-200 rounded-full overflow-hidden ${className}`}
      {...props}
    >
      <div 
        className="h-full bg-blue-600 transition-all duration-300 ease-out rounded-full"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
};

export { Progress };