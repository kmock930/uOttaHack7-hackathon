import './styles/App.css';
import JobDescriptionArea from './components/jobDescriptionArea.tsx';
import DocumentGeneration from './components/DocumentGeneration.tsx';
import DocumentComparison from './components/DocumentComparison.tsx';
import { useState } from 'react';

function App() {
  const [jobDescriptionEntered, setJobDescriptionEntered] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <title>QuickHire</title>
        <center>
          <h1>QuickHire</h1>
          <p>Your Job Application Assistant</p>
        </center>
      </header>
      <JobDescriptionArea 
        setJobDescriptionEntered={setJobDescriptionEntered}
      />
      <DocumentGeneration jobDescriptionEntered={jobDescriptionEntered} />
      <DocumentComparison 
        jobDescriptionEntered={jobDescriptionEntered}
      />
    </div>
  );
}

export default App;
