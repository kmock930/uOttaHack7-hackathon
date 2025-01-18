import { useState, useCallback, ChangeEvent, FC, Dispatch, SetStateAction, useRef } from "react";
import {
  Panel,
  Form,
  FormGroup,
  Radio,
  Button,
  Text,
  Select,
  Box,
  Flex,
  H2,
  H3,
  Grid
} from "@bigcommerce/big-design";
import { Textarea } from "@bigcommerce/big-design";
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import HelpOutline from '@mui/icons-material/HelpOutline';
import styled from "styled-components";
import CircularProgress from '@mui/material/CircularProgress';

interface UploadState {
  file: File | null;
  textContent: string;
  name: string;
  loading?: boolean;
  inputType: "file" | "text" | null;
  error?: string;
}

interface SimilarityScores {
  resume: number | null;
  coverLetter: number | null;
  resumeLoading?: boolean;
  coverLetterLoading?: boolean;
  error?: string;
}

 
type ClearFileParams = {
  setterFn: Dispatch<SetStateAction<UploadState>>;
  setSimilarityScores: Dispatch<SetStateAction<SimilarityScores>>;
  inputRef: React.RefObject<HTMLInputElement>;
} & (
  | { type: "jobDescription" }
  | { type: "resume" | "coverLetter" }
);

const clearFileUpload = (params: ClearFileParams) => {
  const { setterFn, setSimilarityScores, inputRef } = params;

  setterFn({ 
    file: null, 
    name: "", 
    textContent: "",
    inputType: null 
  });
  
  if (inputRef.current) {
    inputRef.current.value = "";
    
    if (params.type === "jobDescription") {
      setSimilarityScores({
        resume: null,
        coverLetter: null,
        resumeLoading: false,
        coverLetterLoading: false
      });
    } else {
      const type = params.type;
      setSimilarityScores(prev => ({ ...prev, [type]: null }));
    }
  }
};

const StyledProgress = styled.progress`
  width: 100%;
  height: 8px;
  margin-top: 12px;
`;

const StyledIconButton = styled(IconButton)`
  padding: 0;
  margin-left: 4px;
`;

const LoadingWrapper = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
`;

const StyledCircularProgress = styled(CircularProgress)`
  color: currentColor;
  width: 20px !important;
  height: 20px !important;
`;

const StyledCompareButton = styled(Button)`
  width: 180px;
  min-height: 40px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const StyledSelect = styled(Select)`
  width: 100%;
  max-width: 300px;
`;

const roleOptions = [
  { value: "software-engineer", content: "Software Engineer" },
  { value: "product-manager", content: "Product Manager" },
  { value: "data-scientist", content: "Data Scientist" },
  { value: "designer", content: "Designer" },
]; 

const fileFormatOptions = [
  { value: "pdf", content: "PDF" },
  { value: "doc", content: "DOC/DOCX" },
];

const ScanningInterface: FC = () => {
  const jobDescriptionInputRef = useRef<HTMLInputElement>(null);
  const resumeInputRef = useRef<HTMLInputElement>(null);
  const coverLetterInputRef = useRef<HTMLInputElement>(null);

  const [selectedRole, setSelectedRole] = useState<string>("");
  const [jobDescription, setJobDescription] = useState<UploadState>({
    file: null,
    textContent: "",
    inputType: null,
    name: "",
  });
  const [generationType, setGenerationType] = useState<"resume" | "coverLetter">
    ("resume");
  const [selectedFormat, setSelectedFormat] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [resumeUpload, setResumeUpload] = useState<UploadState>({
    file: null,
    textContent: "",
    inputType: null,
    name: "",
  });
  const [coverLetterUpload, setCoverLetterUpload] = useState<UploadState>({
    file: null,
    textContent: "",
    inputType: null,
    name: "",
  });
  const [similarityScores, setSimilarityScores] = useState<SimilarityScores>({
    resume: null,
    coverLetter: null,
    resumeLoading: false,
    coverLetterLoading: false,
  });

  const handleFileUpload = useCallback(
    (event: ChangeEvent<HTMLInputElement>, setterFn: (state: UploadState) => void) => {
      const file = event.target.files?.[0];
      if (file) {
        setterFn({ 
          file, 
          name: file.name,
          textContent: "",
          inputType: "file" 
        });
      }
    },
    []
  );

  const handleGenerateDocument = useCallback(async () => {
    if (!jobDescription.file && !jobDescription.textContent) return;
    setGenerating(true);
    setGenerationError(null);  
    try {
      // Mock generation for now - replace with actual API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Add success handling here if needed
    } catch (error) {
      console.error('Document generation error:', error);
      setGenerationError(error instanceof Error ? error.message : "An error occurred");
    } finally {
      setGenerating(false);
    }
  }, [selectedRole, jobDescription.file || jobDescription.textContent, selectedFormat]);

  const handleCompareDocument = useCallback(async (type: "resume" | "coverLetter") => {
    const upload = type === "resume" ? resumeUpload : coverLetterUpload;
    if (!upload.file) return;
    
    setSimilarityScores(prev => ({
      ...prev,
      [`${type}Loading`]: true
    }));

    try {
      // Mock comparison for now - replace with actual API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSimilarityScores(prev => ({
        ...prev,
        [type]: Math.floor(Math.random() * 100),
        [`${type}Loading`]: false,
      }));
    } catch (error) {
      setSimilarityScores(prev => ({
        ...prev,
        [`${type}Loading`]: false,
        error: error instanceof Error ? error.message : "An error occurred"
      }));
    }
  }, [resumeUpload, coverLetterUpload, jobDescription.file, similarityScores]);

  const handleTextChange = useCallback((value: string) => {
    setJobDescription(prev => ({
      ...prev,
      textContent: value
    }));
  }, []);

  return (
    
    <Box marginBottom="xxLarge" marginTop="large">
      <Panel header="Job Details">
        <Form fullWidth>
            <Box padding={"medium"}>
              <Grid
                gridGap="medium"
                alignItems="flex-start"
              >
                <Box>
                  <FormGroup>
                  <Select
                  options={roleOptions}
                  value={selectedRole}
                  required
                  onOptionChange={(value: string) => setSelectedRole(value)}
                  label="Select Role"
                  />
                  </FormGroup>
                </Box>
                <Box>
                  <FormGroup style={{ width: "100%" }}>
                  <Textarea
                    label="Job Description"
                    value={jobDescription.textContent}
                    onChange={(e) => handleTextChange(e.target.value)}
                    disabled={generating || similarityScores.resumeLoading || similarityScores.coverLetterLoading}
                    placeholder="Paste the job description here..."
                    rows={4}
                  />
                  </FormGroup>
                </Box>
                <Box marginTop={"medium"}>
                  <FormGroup>
                  <Box>
                  <Text as="strong" marginBottom="xSmall">Upload Job Description</Text>
                  <input
                    type="file"
                    ref={jobDescriptionInputRef}
                    accept={".pdf,.doc,.docx"}
                    disabled={jobDescription.inputType === "text"}
                    onChange={(e) => handleFileUpload(e, setJobDescription)}
                  />
                  {jobDescription.name && (
                    <Flex alignItems="center" marginTop="xSmall">
                    <Text>{jobDescription.name}</Text>
                    <Button
                      variant="secondary"
                      marginLeft="small"
                      onClick={() => clearFileUpload({
                      setterFn: setJobDescription,
                      setSimilarityScores,
                      inputRef: jobDescriptionInputRef,
                      type: "jobDescription"
                      })}
                      disabled={similarityScores.resumeLoading || similarityScores.coverLetterLoading || generating}
                    >Delete</Button>
                    </Flex>
                  )}
                  <Text color="secondary" marginTop="xSmall">Accepted formats: PDF, DOC, DOCX</Text>
                  </Box>
                </FormGroup>
                </Box>
              </Grid>
            </Box>
        </Form>
      </Panel>
      <Panel header="AI Document Generation" marginTop="large">
        <Box padding="medium">
            <Grid gridColumns="1fr auto" gridGap="medium">
              <Flex flexDirection="column">
                <Text marginBottom="small">Select document type to generate:</Text>
                <Radio
                label="Generate Resume"
                checked={generationType === "resume"}
                onChange={() => setGenerationType("resume")}
                value="resume"
                name="generationType"
                />
                <Radio
                label="Generate Cover Letter"
                checked={generationType === "coverLetter"}
                onChange={() => setGenerationType("coverLetter")}
                value="coverLetter"
                name="generationType"
                />
              </Flex>
              <Box>
                <StyledSelect
                options={fileFormatOptions}
                value={selectedFormat}
                required
                onOptionChange={(value: string) => setSelectedFormat(value)}
                label="Select Output Format"
                />
              </Box>
            </Grid>
           <Flex justifyContent="flex-end" marginTop="medium">
             <StyledCompareButton
               onClick={handleGenerateDocument}
               disabled={!selectedFormat || 
                       generating ||
                       !selectedFormat ||
                      (!jobDescription.file && !jobDescription.textContent)}
               variant="primary"
               marginTop="medium"
             >
              {generating ? "Generating..." : "Generate Document"}
            </StyledCompareButton>
          </Flex>
          {generationError && (
            <Text color="danger" marginTop="small">{generationError}</Text>
          )}
        </Box>
      </Panel>

      <Panel header="Document Comparison" marginTop="large">
        <Flex flexDirection="row" justifyContent="space-between">
          <Box padding="medium">
            <H3>Resume</H3>
            <Flex flexDirection="column" marginTop="small">
              <input
                type="file"
                ref={resumeInputRef}
                data-type="resume"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e, setResumeUpload)}
              />
              {resumeUpload.name && (
                <Flex alignItems="center" marginTop="xSmall">
                  <Text>{resumeUpload.name}</Text>
                  <Button
                    variant="secondary"
                    marginLeft="small"
                    onClick={() => clearFileUpload({
                      setterFn: setResumeUpload,
                      setSimilarityScores,
                      inputRef: resumeInputRef,
                      type: "resume"
                    })}
                    disabled={similarityScores.resumeLoading || similarityScores.coverLetterLoading || generating}                    
                  >Delete</Button>
                </Flex>
              )}
              <Text color="secondary" marginTop="xSmall">
                Accepted formats: PDF, DOC, DOCX
              </Text>
            </Flex>
            {similarityScores.resume !== null && (
              <Box marginTop="medium">
                <Flex>
                  <Text>Strength</Text>
                  <Tooltip title="Similarity with Job Description" placement="top" arrow>
                    <StyledIconButton size="small">
                      <HelpOutline fontSize="inherit" />
                    </StyledIconButton>
                  </Tooltip>
                </Flex>
                <StyledProgress
                  value={similarityScores.resume}
                  max={100}
                />
              </Box>
            )}
            <StyledCompareButton
              variant="primary"
              disabled={!resumeUpload.file || !jobDescription.file || similarityScores.resumeLoading}
              onClick={() => handleCompareDocument("resume")}
              marginTop="medium"
              margin="none"
            >
              {similarityScores.resumeLoading ? (
                <StyledCircularProgress />
              ) : 'Compare Resume'}
            </StyledCompareButton>
          </Box>

          <Box padding="medium">
            <H3>Cover Letter</H3>
            <Flex flexDirection="column" marginTop="small">
              <input
                type="file"
                ref={coverLetterInputRef}
                data-type="coverLetter"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e, setCoverLetterUpload)}
              />
              {coverLetterUpload.name && (
                <Flex alignItems="center" marginTop="xSmall">
                  <Text>{coverLetterUpload.name}</Text>
                  <Button
                    variant="secondary"
                    marginLeft="small"
                    onClick={() => clearFileUpload({
                      setterFn: setCoverLetterUpload,
                      setSimilarityScores,
                      inputRef: coverLetterInputRef,
                      type: "coverLetter"
                    })}
                    disabled={similarityScores.resumeLoading || similarityScores.coverLetterLoading || generating}                    
                  >Delete</Button>
                </Flex>
              )}
              <Text color="secondary">
                Accepted formats: PDF, DOC, DOCX
              </Text>
            </Flex>
            {similarityScores.coverLetter !== null && (
              <Box marginTop="medium">
                <Flex>
                  <Text>Strength</Text>
                  <Tooltip title="Similarity with Job Description" placement="top" arrow>
                    <StyledIconButton size="small">
                      <HelpOutline fontSize="inherit" />
                    </StyledIconButton>
                  </Tooltip>
                </Flex>
                <StyledProgress
                  value={similarityScores.coverLetter}
                  max={100}
                />
              </Box>
            )}
            <StyledCompareButton
              variant="primary"
              disabled={!coverLetterUpload.file || !jobDescription.file || similarityScores.coverLetterLoading}
              onClick={() => handleCompareDocument("coverLetter")}
              marginTop="medium"
              margin="none"
            >
              {similarityScores.coverLetterLoading ? (
                <LoadingWrapper><StyledCircularProgress /></LoadingWrapper>
              ) : 'Compare Cover Letter'}
            </StyledCompareButton>
          </Box>
        </Flex>
        {similarityScores.error && (
          <Text color="danger" marginTop="medium">
            {similarityScores.error}
          </Text>
        )}
      </Panel>
    </Box>
  );
}; 
 
export default ScanningInterface;
