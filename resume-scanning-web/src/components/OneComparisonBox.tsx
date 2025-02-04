import React, { useState, useEffect } from 'react';
import '../styles/OneComparisonBox.css';
import FileUploadHook from '../hooks/fileUploadHook.tsx';
import { Button, IconButton, Tooltip } from '@mui/material';

export default function OneComparisonBox({ documentType, jobDescriptionEntered }) {
    const [uploadedFile, setUploadedFile] = useState(null);
    const [similarity, setSimilarity] = useState<number | null>(null);
    const [showSimilarityBar, setShowSimilarityBar] = useState(false);

    const handleCompare = () => {
        setSimilarity(70);
        setShowSimilarityBar(true);
    }

    useEffect(() => {
        if (!uploadedFile) {
            setSimilarity(null);
            setShowSimilarityBar(false);
        }
    }, [uploadedFile]);

    return (
        <div>
            <h2>
                {documentType}
            </h2>
            <FileUploadHook uploadedFile={uploadedFile} setUploadedFile={setUploadedFile} />
            {uploadedFile != null && similarity !== null && showSimilarityBar && (
                <div className="similarity-container">
                    <span className="similarity-score">
                        Strength of {documentType}: {similarity}%
                    </span>
                    <IconButton>
                        <Tooltip title={`This bar indicates the strength of your ${documentType.toLowerCase()} - the similarity score in %.`}>
                            <span role="img" aria-label="light bulb">💡</span>
                        </Tooltip>
                    </IconButton>
                    <div className="similarity-bar-container">
                        <div
                            className="similarity-bar"
                            style={{ width: `${similarity}%` }}
                        />
                    </div>
                    <br />
                </div>
            )}
            <Button variant="contained" color="primary" className="compare-button" onClick={handleCompare} disabled={!jobDescriptionEntered || !uploadedFile}>
                Compare {documentType}
            </Button>
        </div>
    );
}