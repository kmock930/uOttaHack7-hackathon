import { Box, Panel, Flex, H1 } from "@bigcommerce/big-design";
import ScanningInterface from "../components/ScanningInterface";
  
 

   
export default function Index() {
  return (
    <Box aria-label="Resume scanning interface container">
      <Flex flexDirection="column" alignItems="center">
        <Box maxWidth="1200px" width="100%" padding="medium">
          <H1 marginBottom="medium">Resume Scanning Assistant</H1>
          
          <Panel>
            <Box 
              padding={{ mobile: "medium", tablet: "large" }}
              marginHorizontal="auto"
              maxWidth="900px"
            >
              <ScanningInterface />
            </Box>
          </Panel>
        </Box>
      </Flex>
    </Box>
  );
}
