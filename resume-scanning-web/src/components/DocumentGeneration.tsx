import { Box, Button, Radio, Select } from '@mui/material';
import MenuItem from '@mui/material/MenuItem';
import React, { useEffect } from 'react';
import { FormControl, FormLabel, RadioGroup, FormControlLabel } from '@mui/material';
import '../styles/DocumentGeneration.css';
import { useState } from 'react';

export default function DocumentGeneration({ jobDescriptionEntered }) {
  const fileFormatOptions = ["PDF", "DOC/DOCX", "LaTex"];
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);
  const [documentType, setDocumentType] = useState("Resume");
  const [outputFormat, setOutputFormat] = useState("");

  useEffect(() => {
    setIsButtonDisabled(!(jobDescriptionEntered && documentType && outputFormat));
  }, [jobDescriptionEntered, documentType, outputFormat]);

  return (
    <div className="DocumentGeneration">
      <h1 className="h1">Document Generation</h1>
      <Box position="relative">
        <FormControl>
          <FormLabel id="form-label-document-type">Select a document type to generate</FormLabel>
          <RadioGroup
            aria-labelledby="radio-document-type"
            defaultValue="Resume"
            name="radio-buttons-group"
            onChange={(e) => setDocumentType(e.target.value)}
          >
            <FormControlLabel value="Resume" control={<Radio />} label="Resume" />
            <FormControlLabel value="Cover Letter" control={<Radio />} label="Cover Letter" />
          </RadioGroup>
        </FormControl>
        <FormControl className="output-format-form" style={{marginTop: 20, right: 0, position: 'absolute'}}>
          <FormLabel id="form-label-output-format">Select Output Format</FormLabel>
          <Select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value as string)}>
            {
              fileFormatOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))
            }
          </Select>
        </FormControl>
      </Box>
      <div className="button-container">
        <Button 
          variant="contained" 
          color="primary" 
          className="generate-button" 
          disabled={isButtonDisabled}
        >
          Generate Document
        </Button>
      </div>
    </div>
  );
}