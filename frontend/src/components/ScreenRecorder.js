import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Video, 
  Square, 
  Play, 
  Pause, 
  Trash2, 
  Download,
  Monitor,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

const ScreenRecorder = ({ 
  questionId, 
  onRecordingComplete, 
  maxDuration = 1800, // 30 minutes default
  existingRecording = null,
  disabled = false 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState(existingRecording);
  const [recordingSize, setRecordingSize] = useState(0);
  const [error, setError] = useState('');
  const [isSupported, setIsSupported] = useState(true);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const videoRef = useRef(null);

  const MAX_SIZE_BYTES = 1024 * 1024 * 1024; // 1GB
  const MAX_SIZE_MB = 1024; // 1GB in MB

  useEffect(() => {
    // Check if screen recording is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      setIsSupported(false);
      setError('Screen recording is not supported in this browser. Please use Chrome, Firefox, or Edge.');
    }

    return () => {
      stopRecording();
      clearInterval(timerRef.current);
    };
  }, []);

  useEffect(() => {
    // Load existing recording from localStorage
    if (questionId && !existingRecording) {
      const savedRecording = localStorage.getItem(`screen_recording_${questionId}`);
      if (savedRecording) {
        try {
          const recordingData = JSON.parse(savedRecording);
          if (recordingData.blob) {
            // Convert base64 back to blob
            const byteCharacters = atob(recordingData.blob);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
              byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'video/webm' });
            setRecordedBlob(blob);
            setRecordingDuration(recordingData.duration || 0);
            setRecordingSize(recordingData.size || 0);
          }
        } catch (err) {
          console.error('Error loading saved recording:', err);
        }
      }
    }
  }, [questionId, existingRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const startRecording = async () => {
    try {
      setError('');
      
      // Request screen capture
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          mediaSource: 'screen',
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          frameRate: { ideal: 30, max: 60 }
        },
        audio: false // No microphone audio as requested
      });

      streamRef.current = stream;
      chunksRef.current = [];
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9' // Use VP9 for better compression
      });
      
      mediaRecorderRef.current = mediaRecorder;

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          
          // Calculate current size
          const currentSize = chunksRef.current.reduce((total, chunk) => total + chunk.size, 0);
          setRecordingSize(currentSize);
          
          // Check if size exceeds 1GB
          if (currentSize > MAX_SIZE_BYTES) {
            stopRecording();
            setError('Recording stopped: Maximum file size (1GB) reached.');
          }
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        setRecordedBlob(blob);
        saveRecording(blob, recordingDuration, blob.size);
        
        if (onRecordingComplete) {
          onRecordingComplete(blob, recordingDuration);
        }
      };

      // Handle stream end (user stops sharing)
      stream.getVideoTracks()[0].onended = () => {
        if (isRecording) {
          stopRecording();
        }
      };

      // Start recording
      mediaRecorder.start(1000); // Record in 1-second chunks
      setIsRecording(true);
      setIsPaused(false);
      setRecordingDuration(0);
      setRecordingSize(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingDuration(prev => {
          const newDuration = prev + 1;
          if (newDuration >= maxDuration) {
            stopRecording();
            setError(`Recording stopped: Maximum duration (${Math.floor(maxDuration / 60)} minutes) reached.`);
          }
          return newDuration;
        });
      }, 1000);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please make sure you grant screen sharing permission.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        timerRef.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        clearInterval(timerRef.current);
      }
      setIsPaused(!isPaused);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    clearInterval(timerRef.current);
    setIsRecording(false);
    setIsPaused(false);
  };

  const saveRecording = (blob, duration, size) => {
    if (!questionId) return;

    try {
      // Convert blob to base64 for localStorage
      const reader = new FileReader();
      reader.onload = () => {
        const base64Data = reader.result.split(',')[1];
        const recordingData = {
          blob: base64Data,
          duration: duration,
          size: size,
          timestamp: new Date().toISOString(),
          mimeType: blob.type
        };
        
        localStorage.setItem(`screen_recording_${questionId}`, JSON.stringify(recordingData));
      };
      reader.readAsDataURL(blob);
    } catch (err) {
      console.error('Error saving recording:', err);
      setError('Failed to save recording locally.');
    }
  };

  const deleteRecording = () => {
    setRecordedBlob(null);
    setRecordingDuration(0);
    setRecordingSize(0);
    setError('');
    
    if (questionId) {
      localStorage.removeItem(`screen_recording_${questionId}`);
    }
    
    if (onRecordingComplete) {
      onRecordingComplete(null, 0);
    }
  };

  const downloadRecording = () => {
    if (recordedBlob) {
      const url = URL.createObjectURL(recordedBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screen_recording_${questionId || 'recording'}_${new Date().toISOString().slice(0, 19)}.webm`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  if (!isSupported) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-4">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <div>
              <h4 className="font-medium text-red-900">Screen Recording Not Supported</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Recording Controls */}
      <Card className={`border-2 ${isRecording ? 'border-red-300 bg-red-50' : 'border-blue-300 bg-blue-50'}`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isRecording ? 'bg-red-100' : 'bg-blue-100'
              }`}>
                {isRecording ? (
                  <div className="w-4 h-4 bg-red-600 rounded-full animate-pulse" />
                ) : (
                  <Monitor className={`w-6 h-6 ${isRecording ? 'text-red-600' : 'text-blue-600'}`} />
                )}
              </div>
              <div>
                <h3 className={`font-medium ${isRecording ? 'text-red-900' : 'text-blue-900'}`}>
                  Screen Recording
                </h3>
                <p className={`text-sm ${isRecording ? 'text-red-700' : 'text-blue-700'}`}>
                  {isRecording 
                    ? (isPaused ? 'Recording Paused' : 'Recording in Progress') 
                    : 'Click to start recording your screen'
                  }
                </p>
              </div>
            </div>
            
            {isRecording && (
              <div className="text-right">
                <div className={`text-lg font-mono font-bold ${isPaused ? 'text-orange-600' : 'text-red-600'}`}>
                  {formatTime(recordingDuration)}
                </div>
                <div className="text-xs text-gray-600">
                  {formatFileSize(recordingSize)} / {MAX_SIZE_MB}MB max
                </div>
              </div>
            )}
          </div>

          {/* Progress Bar for Recording */}
          {isRecording && (
            <div className="mb-4">
              <Progress 
                value={(recordingDuration / maxDuration) * 100} 
                className="h-2"
              />
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>Duration: {formatTime(recordingDuration)}</span>
                <span>Max: {formatTime(maxDuration)}</span>
              </div>
            </div>
          )}

          {/* Control Buttons */}
          <div className="flex items-center space-x-3">
            {!isRecording && !recordedBlob && (
              <Button 
                onClick={startRecording}
                disabled={disabled}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                <Video className="w-4 h-4 mr-2" />
                Start Recording
              </Button>
            )}

            {isRecording && (
              <>
                <Button 
                  onClick={pauseRecording}
                  variant="outline"
                  className="border-orange-300 text-orange-700 hover:bg-orange-50"
                >
                  {isPaused ? <Play className="w-4 h-4 mr-2" /> : <Pause className="w-4 h-4 mr-2" />}
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                
                <Button 
                  onClick={stopRecording}
                  className="bg-gray-600 hover:bg-gray-700 text-white"
                >
                  <Square className="w-4 h-4 mr-2" />
                  Stop Recording
                </Button>
              </>
            )}

            {!isRecording && recordedBlob && (
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Recording Complete
                </Badge>
                <span className="text-sm text-gray-600">
                  {formatTime(recordingDuration)} • {formatFileSize(recordingSize)}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-3">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recording Playback */}
      {recordedBlob && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900">Recorded Video</h4>
              <div className="flex items-center space-x-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={downloadRecording}
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </Button>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={deleteRecording}
                  className="text-red-600 hover:text-red-700 border-red-300"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </Button>
              </div>
            </div>
            
            <video 
              ref={videoRef}
              controls 
              className="w-full max-h-96 bg-black rounded-lg"
              src={recordedBlob ? URL.createObjectURL(recordedBlob) : ''}
            />
            
            <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  Duration: {formatTime(recordingDuration)}
                </span>
                <span>Size: {formatFileSize(recordingSize)}</span>
              </div>
              <Badge variant="outline" className="bg-green-50 text-green-700">
                Ready for Submission
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <h4 className="font-medium text-gray-900 mb-2">📋 Recording Instructions</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Click "Start Recording" and select the screen/window to share</li>
            <li>• Your recording will be automatically saved locally</li>
            <li>• Maximum recording time: {Math.floor(maxDuration / 60)} minutes</li>
            <li>• Maximum file size: 1GB (recording stops automatically if exceeded)</li>
            <li>• You can pause/resume recording as needed</li>
            <li>• Use "Download" to save the recording to your device</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default ScreenRecorder;