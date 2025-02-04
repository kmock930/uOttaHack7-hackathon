import React, { useState, useEffect } from 'react';
import '../styles/jobDescriptionArea.css';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { TextareaAutosize } from '@mui/material';
import FileUploadHook from '../hooks/fileUploadHook.tsx';

export default function JobDescriptionArea({ setJobDescriptionEntered }) {
  const roleList = ["Software Engineer", "Data Scientist", "Product Manager", "UX Designer", "QA Engineer"];
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  useEffect(() => {
    setJobDescriptionEntered(uploadedFile !== null || jobDescription.trim().length > 0);
  }, [uploadedFile, jobDescription, setJobDescriptionEntered]);

  return (
    <div className="jobDescriptionArea">
      <h1>Job Details</h1>
      <Autocomplete
        disablePortal
        options={roleList}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Roles" />}
      />
      <TextareaAutosize
        minRows={5}
        placeholder="Job Description (optional)"
        disabled={uploadedFile !== null}
        style={{ width: 300, marginTop: 20 }}
        onChange={(e) => setJobDescription(e.target.value)}
      />
      <br />
      <FileUploadHook uploadedFile={uploadedFile} setUploadedFile={setUploadedFile} />
    </div>
  );
}