import { useState, useCallback, ChangeEvent, FC } from "react";
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
  Grid,
} from "@bigcommerce/big-design";
 
interface UploadState {
  file: File | null;
  name: string;
  loading?: boolean;
  error?: string;
}

interface SimilarityScores {
  resume: number | null;
  coverLetter: number | null;
  error?: string;
}

const roleOptions = [
  { value: "software-engineer", content: "Software Engineer" },
  { value: "product-manager", content: "Product Manager" },
  { value: "data-scientist", content: "Data Scientist" },
  { value: "designer", content: "Designer" },
];

 
const ScanningInterface: FC = () => {
  const [selectedRole, setSelectedRole] = useState<string>(""
);
  const [jobDescription, setJobDescription] = useState<UploadState>({
    file: null,
    name: "",
  });
  const [generationType, setGenerationType] = useState<"resume" | "coverLetter">
(  "resume"
  );
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [resumeUpload, setResumeUpload] = useState<UploadState>({
    file: null,
    name: "",
  });
  const [coverLetterUpload, setCoverLetterUpload] = useState<UploadState>({
    file: null,
    name: "",
  });
  const [similarityScores, setSimilarityScores] = useState<SimilarityScores>({
    resume: null,
    coverLetter: null,
  });

  const handleFileUpload = useCallback(
    (event: ChangeEvent<HTMLInputElement>, setterFn: (state: UploadState) => void) => {
      const file = event.target.files?.[0];
      if (file) {
        setterFn({ file, name: file.name });
      }
    },
    []
  );

  const handleGenerateDocument = useCallback(async () => {
    if (!selectedRole || !jobDescription.file) return;
    setGenerating(true);
    setGenerationError(null);
    try {
      // Mock generation for now - replace with actual API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Success handling will go here
    } catch (error) {
      setGenerationError(error instanceof Error ? error.message : "An error occurred");
    } finally {
      setGenerating(false);
    }
  }, [selectedRole, jobDescription.file]);

  const handleCompareDocument = useCallback(async (type: "resume" | "coverLetter") => {
    const upload = type === "resume" ? resumeUpload : coverLetterUpload;
    if (!upload.file || !jobDescription.file) return;
    const newScores = { ...similarityScores };
    try {
      // Mock comparison for now - replace with actual API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      newScores[type] = Math.floor(Math.random() * 100);
      setSimilarityScores(newScores);
    } catch (error) {
      setSimilarityScores({
        ...newScores,
        error: error instanceof Error ? error.message : "An error occurred"
      });
    }
  }, [resumeUpload, coverLetterUpload, jobDescription.file, similarityScores]);

  return (
    <Box marginBottom="xxLarge">
      <Panel header="Job Details">
        <Form>
          <Flex justifyContent="space-between" alignItems="flex-start">
            <FormGroup labelText="Select Role">
              <Select
                options={roleOptions}
                value={selectedRole}
                required
                onOptionChange={(value: string) => setSelectedRole(value)}
              />
            </FormGroup>
            <FormGroup labelText="Upload Job Description">
              <Box marginBottom="xSmall">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => handleFileUpload(e, setJobDescription)}
                />
                {jobDescription.name && <Text>{jobDescription.name}</Text>}
              </Box>
              <Text color="secondary">Accepted formats: PDF, DOC, DOCX</Text>
            </FormGroup>
          </Flex>
        </Form>
      </Panel>
      <Panel header="AI Document Generation" marginTop="medium">
        <Box>
          <Flex flexDirection="column">
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
          <Flex justifyContent="flex-end">
            <Button
              onClick={handleGenerateDocument}
              disabled={!selectedRole || !jobDescription.file || generating}
              isLoading={generating}
            >
              Generate Document
            </Button>
          </Flex>
          {generationError && (
            <Text color="danger" marginTop="small">{generationError}</Text>
          )}
        </Box>
      </Panel>

      <Panel header="Document Comparison" marginTop="medium">
        <Grid gridColumns="1fr 1fr" gridGap="medium">
          <Box>
            <H3>Resume</H3>
            <Flex flexDirection="column">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e, setResumeUpload)}
              />
              {resumeUpload.name && <Text>{resumeUpload.name}</Text>}
              <Text color="secondary">
                Accepted formats: PDF, DOC, DOCX
              </Text>
            </Flex>
            {similarityScores.resume !== null && (
              <Text marginBottom="small">Similarity Score: {similarityScores.resume}%</Text>
            )}
            <Button
              variant="primary"
              disabled={!resumeUpload.file || !jobDescription.file}
              onClick={() => handleCompareDocument("resume")}
              marginTop="medium"
            >
              Compare Resume
            </Button>
          </Box>

          <Box>
            <H3>Cover Letter</H3>
            <Flex flexDirection="column">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e, setCoverLetterUpload)}
              />
              {coverLetterUpload.name && <Text>{coverLetterUpload.name}</Text>}
              <Text color="secondary">
                Accepted formats: PDF, DOC, DOCX
              </Text>
            </Flex>
            {similarityScores.coverLetter !== null && (
              <Text marginBottom="small">Similarity Score: {similarityScores.coverLetter}%</Text>
            )}
            <Button
              variant="primary"
              disabled={!coverLetterUpload.file || !jobDescription.file}
              onClick={() => handleCompareDocument("coverLetter")}
              marginTop="medium"
            >
              Compare Cover Letter
            </Button>
          </Box>
        </Grid>
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
