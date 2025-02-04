import React from 'react';
import '../styles/DocumentComparison.css';
import { Box } from '@mui/material';
import OneComparisonBox from './OneComparisonBox.tsx';

export default function DocumentComparison({ jobDescriptionEntered }) {

    return (
        <div className="DocumentComparison">
            <h1 className="h1" >Document Comparison</h1>
            <Box display="flex" justifyContent="space-between">
                <OneComparisonBox documentType="Resume" jobDescriptionEntered={jobDescriptionEntered} />
                <OneComparisonBox documentType="Cover Letter" jobDescriptionEntered={jobDescriptionEntered} />
            </Box>
        </div>
    )
}