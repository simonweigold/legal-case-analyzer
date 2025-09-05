// components/InputSidebar/InputSidebar.tsx
import React, { useState, useRef } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  Typography,
  Button,
  TextField,
  Divider,
  Paper,
  Alert,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Upload,
  Description,
  PictureAsPdf,
  Delete,
  Clear,
  Send,
  CloudUpload,
  FileUpload
} from '@mui/icons-material';

export interface InputSidebarProps {
  open: boolean;
  onToggle: () => void;
  onTextSubmit: (text: string, source: 'text' | 'pdf', filename?: string) => void;
  isProcessing?: boolean;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  text?: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  error?: string;
}

const DRAWER_WIDTH = 350;

export function InputSidebar({
  open,
  onToggle,
  onTextSubmit,
  isProcessing = false
}: InputSidebarProps) {
  const [textInput, setTextInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Convert PDF to text (mock implementation - replace with actual PDF parsing)
  const extractTextFromPDF = async (file: File): Promise<string> => {
    // This is a mock implementation. In production, you'd use a library like pdf-parse
    // or send the file to a backend service for processing
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (file.name.toLowerCase().includes('error')) {
          reject(new Error('Failed to extract text from PDF'));
        } else {
          resolve(`[EXTRACTED TEXT FROM ${file.name}]\n\nThis is mock extracted text from the PDF file. In a real implementation, this would contain the actual text content extracted from the PDF document using a library like pdf-parse or a backend service.\n\nThe text would include all the readable content from the PDF, including headings, paragraphs, and other textual elements while maintaining reasonable formatting.`);
        }
      }, 2000); // Simulate processing time
    });
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Check file type
      if (!file.type.includes('pdf') && !file.type.includes('text')) {
        alert(`File ${file.name} is not a PDF or text file`);
        continue;
      }

      const fileId = crypto.randomUUID();
      const uploadedFile: UploadedFile = {
        id: fileId,
        name: file.name,
        size: file.size,
        status: 'uploading'
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);

      try {
        let extractedText = '';
        
        // Update status to processing
        setUploadedFiles(prev => 
          prev.map(f => f.id === fileId ? { ...f, status: 'processing' } : f)
        );

        if (file.type.includes('pdf')) {
          extractedText = await extractTextFromPDF(file);
        } else {
          // Handle text files
          extractedText = await file.text();
        }

        // Update with extracted text
        setUploadedFiles(prev => 
          prev.map(f => f.id === fileId ? { 
            ...f, 
            status: 'ready', 
            text: extractedText 
          } : f)
        );

      } catch (error) {
        setUploadedFiles(prev => 
          prev.map(f => f.id === fileId ? { 
            ...f, 
            status: 'error', 
            error: error instanceof Error ? error.message : 'Unknown error'
          } : f)
        );
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileUpload(e.target.files);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmitText = () => {
    if (textInput.trim()) {
      onTextSubmit(textInput.trim(), 'text');
      setTextInput('');
    }
  };

  const handleSubmitFile = (file: UploadedFile) => {
    if (file.text) {
      onTextSubmit(file.text, 'pdf', file.name);
      // Optionally remove the file after submission
      // setUploadedFiles(prev => prev.filter(f => f.id !== file.id));
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const clearAllFiles = () => {
    setUploadedFiles([]);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const drawerContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" component="h2" sx={{ fontWeight: 600, fontSize: '1.1rem' }}>
          Document Input
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
          Upload PDFs or paste text
        </Typography>
      </Box>

      {/* Text Input Section */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Paste Court Decision Text
        </Typography>
        <TextField
          multiline
          rows={6}
          fullWidth
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Paste the full text of a court decision, legal document, or case law here..."
          variant="outlined"
          size="small"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          startIcon={<Send />}
          onClick={handleSubmitText}
          disabled={!textInput.trim() || isProcessing}
          fullWidth
          size="small"
        >
          Analyze Text
        </Button>
      </Box>

      <Divider />

      {/* File Upload Section */}
      <Box sx={{ p: 2, flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle2">
            Upload PDF Documents
          </Typography>
          {uploadedFiles.length > 0 && (
            <Button
              size="small"
              startIcon={<Clear />}
              onClick={clearAllFiles}
              color="secondary"
            >
              Clear All
            </Button>
          )}
        </Box>

        {/* Drop Zone */}
        <Paper
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          sx={{
            p: 3,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: dragOver ? 'primary.main' : 'divider',
            backgroundColor: dragOver ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            mb: 2,
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover'
            }
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <CloudUpload sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Drop PDF files here or click to browse
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Supports PDF and TXT files
          </Typography>
        </Paper>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileInputChange}
        />

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            <List dense>
              {uploadedFiles.map((file) => (
                <ListItem key={file.id} sx={{ px: 0 }}>
                  <Box sx={{ width: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PictureAsPdf sx={{ mr: 1, fontSize: 20, color: 'error.main' }} />
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography variant="body2" noWrap>
                          {file.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatFileSize(file.size)}
                        </Typography>
                      </Box>
                      <IconButton
                        size="small"
                        onClick={() => removeFile(file.id)}
                        sx={{ ml: 1 }}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                    
                    {/* Status Indicator */}
                    <Box sx={{ mb: 1 }}>
                      {file.status === 'uploading' && (
                        <Chip label="Uploading..." size="small" color="info" />
                      )}
                      {file.status === 'processing' && (
                        <>
                          <Chip label="Extracting text..." size="small" color="warning" />
                          <LinearProgress sx={{ mt: 1, height: 2 }} />
                        </>
                      )}
                      {file.status === 'ready' && (
                        <>
                          <Chip label="Ready" size="small" color="success" />
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<Send />}
                            onClick={() => handleSubmitFile(file)}
                            disabled={isProcessing}
                            sx={{ mt: 1, fontSize: '0.7rem' }}
                          >
                            Analyze PDF
                          </Button>
                        </>
                      )}
                      {file.status === 'error' && (
                        <Alert severity="error" sx={{ mt: 1, py: 0 }}>
                          <Typography variant="caption">
                            {file.error}
                          </Typography>
                        </Alert>
                      )}
                    </Box>
                  </Box>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary" display="block">
          Supported formats: PDF, TXT
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Max file size: 10MB per file
        </Typography>
      </Box>
    </Box>
  );

  return (
    <>
      {/* Menu Button - only show when sidebar is closed */}
      {!open && (
        <IconButton
          onClick={onToggle}
          sx={{
            position: 'fixed',
            top: 16,
            left: 16,
            zIndex: 1201,
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            boxShadow: 3,
            '&:hover': {
              backgroundColor: 'primary.dark',
            }
          }}
        >
          <FileUpload />
        </IconButton>
      )}

      {/* Drawer */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={open}
        onClose={onToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
}
