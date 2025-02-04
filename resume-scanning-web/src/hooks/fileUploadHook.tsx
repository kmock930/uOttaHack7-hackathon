import React, { useRef } from 'react';
import { Button } from '@mui/material';

export default function FileUploadHook({ uploadedFile, setUploadedFile }) {
    const fileInputRef = useRef(null);

    const handleFileUpload = (e) => {
        const file = e.target.files?.[0];
        if (file) {
          setUploadedFile(file);
          console.log(`File selected: ${file.name}`);
        }
    };

    const handleFileDelete = () => {
        setUploadedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        console.log('File deleted');
    };

    return (
        <div>
            <input
                type="file"
                accept=".txt,.pdf,.doc,.docx"
                style={{ marginTop: 20 }}
                onChange={(e) => handleFileUpload(e)}
                ref={fileInputRef}
            />
            {uploadedFile && (
                <div style={{ marginTop: 20 }}>
                <span>{uploadedFile.name}</span>
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleFileDelete}
                    style={{ marginLeft: 10 }}
                >
                    Delete
                </Button>
                </div>
            )}
            <p style={{ marginTop: 10, color: 'grey', fontSize: '0.8em', fontStyle: 'italic' }}>Accepted file formats: .txt, .pdf, .doc, .docx</p>
        </div>
    )
}