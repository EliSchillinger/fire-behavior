import { useState } from 'react';
import DOMPurify from 'dompurify';
import cyverse_waiting from './assets/cyverse_loading.gif';
import './App.css';

function App() {
  const [inputValue, setInputValue] = useState('');
  
  const [htmlContent, setHtmlContent] = useState('<p></p>');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleProcessInput = async () => {
    setIsLoading(true);
    setHtmlContent('');

    try {
      console.log("Making Post request")
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: inputValue }),
      });
      console.log("Post request made")

      setInputValue('');

      const data = await res.json();
      console.log("Data received, sanatizing: " + data)
      const sanitizedHtml = DOMPurify.sanitize(data.response, {
        ADD_TAGS: ['iframe'],
        ADD_ATTR: ['src', 'title', 'style', 'allowfullscreen', 'frameborder', 'scrolling']
      });
      
      console.log("Data sanitized, " + sanitizedHtml + ", setting html content")
      setHtmlContent(sanitizedHtml);

    } catch (err) {
      console.error('Error calling backend:', err);
      setHtmlContent("<p style='color: red;'>Failed to fetch data...</p>");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && inputValue.trim() !== '') {
      handleProcessInput();
    }
  };

  return (
    <div className="App">
      <div className="Header">
        Fire Behavior Machine
      </div>
      <div className="Body">
        {isLoading ? (
          <div className="loading-container">
            <img src={cyverse_waiting} alt="Loading..." id="loadingIcon" />
          </div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
        )}
      </div>
      <input 
        type="text" 
        id="prompt" 
        value={inputValue} 
        onChange={handleInputChange} 
        onKeyDown={handleKeyPress} 
        placeholder="Enter a prompt here"
        disabled={isLoading}
      />
    </div>
  );
}

export default App;