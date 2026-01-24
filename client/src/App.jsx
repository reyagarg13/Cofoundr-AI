import React, { useState, useEffect, useRef } from 'react';
import { generatePitchDeck, generateDetailedPitchDeck, checkServerHealth, validateStartupIdea } from './services/api';
import LandingSection from './components/LandingSection';
import LoadingSpinner from './components/LoadingSpinner';
import LogoGenerator from './components/LogoGenerator';
import WebsiteGenerator from './components/WebsiteGenerator';
import { downloadPDF, validateContentForPDF, previewPDFStructure } from './utils/pdfGenerator';

function App() {
  // Tab management
  const [activeTab, setActiveTab] = useState('pitch-deck');
  
  // Pitch deck states
  const [pitchDeck, setPitchDeck] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');
  const [serverStatus, setServerStatus] = useState('checking');
  const [businessIdea, setBusinessIdea] = useState('');
  const [businessModel, setBusinessModel] = useState('B2C');
  const [industry, setIndustry] = useState('Technology');
  const [targetMarket, setTargetMarket] = useState('Young Adults (18-30)');
  const [fundingStage, setFundingStage] = useState('Pre-Seed');
  const [useDetailed, setUseDetailed] = useState(false);
  const [ideaValidation, setIdeaValidation] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);
  const [generateDetailed, setGenerateDetailed] = useState(false);
  const [targetAudience, setTargetAudience] = useState('general investors');
  const [showLanding, setShowLanding] = useState(true);
  const [copySuccess, setCopySuccess] = useState(false);
  const [isMockMode, setIsMockMode] = useState(false);
  const [presentationStyle, setPresentationStyle] = useState('balanced');
  const [competitorContext, setCompetitorContext] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('');
  const [pdfDownloading, setPdfDownloading] = useState(false);
  
  // Refs
  const containerRef = useRef(null);
  const formRef = useRef(null);

  // Sample ideas for inspiration
  const sampleIdeas = [
    "A mobile app that helps students find part-time internships based on their skill set and location",
    "An AI-powered fitness platform that creates personalized workout plans for seniors",
    "A sustainable food delivery service using electric bikes and eco-friendly packaging",
    "A blockchain-based platform for freelancers to showcase verified skills and get hired",
    "A virtual reality meditation app that creates immersive relaxation experiences",
    "A smart home security system that uses AI to detect unusual activities",
    "An online marketplace for local farmers to sell directly to consumers"
  ];

  // Check server health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkServerHealth();
        console.log('Health check result:', health);
        
        if (health.status === 'healthy') {
          setServerStatus('online');
          setIsMockMode(!!health.mock_mode);
        } else if (health.status === 'timeout') {
          setServerStatus('busy'); // Server is running but slow
        } else {
          setServerStatus('offline');
        }
      } catch (error) {
        console.error('Health check failed:', error);
        setServerStatus('offline');
      }
    };
    
    // Initial health check
    checkHealth();
    
    // Check every 15 seconds (reduced frequency to avoid overwhelming server)
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    // Validate idea
    const validation = validateStartupIdea(businessIdea);
    if (!validation.isValid) {
      setOutput(`❌ ${validation.error}`);
      return;
    }

    // Check server status before proceeding
    if (serverStatus === 'offline') {
      setOutput('❌ Server is offline. Please make sure the server is running and try again.');
      return;
    }

    setLoading(true);
    setLoadingMessage(generateDetailed ? 
      '🔍 Analyzing your startup idea for detailed pitch deck...' : 
      '🚀 Crafting your professional pitch deck...'
    );
    setOutput('');
    
    try {
      const options = {
        target_audience: targetAudience,
        industry: industry || null,
        funding_stage: fundingStage,
        presentation_style: presentationStyle,
        business_model: businessModel || null,
        competitor_context: competitorContext || null,
        // Add timestamp and random element to ensure unique requests
        request_id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      };

      console.log("🔍 DEBUG: Generation options:", options);
      console.log("🎯 DEBUG: Idea:", businessIdea);
      console.log("📊 DEBUG: Generate detailed:", generateDetailed);

      // Update loading message during process
      setTimeout(() => {
        if (loading) {
          setLoadingMessage(generateDetailed ? 
            '📊 Creating comprehensive market analysis and financial projections...' : 
            '✨ Generating compelling slides and content...'
          );
        }
      }, 3000);

      setTimeout(() => {
        if (loading) {
          setLoadingMessage('🎯 Finalizing your investor-ready pitch deck...');
        }
      }, 6000);

      const result = generateDetailed 
        ? await generateDetailedPitchDeck(businessIdea, options)
        : await generatePitchDeck(businessIdea, options);
      
      console.log("Pitch deck result:", result);
      
      // Check if result contains error message
      if (typeof result === 'string' && result.includes('❌')) {
        setOutput(result);
        // Update server status if connection issues detected
        if (result.includes('Cannot connect') || result.includes('ECONNREFUSED')) {
          setServerStatus('offline');
        } else if (result.includes('timeout') || result.includes('temporarily unavailable')) {
          setServerStatus('busy');
        }
      } else {
        setOutput(result);
        // Update server status to online if request succeeded
        if (serverStatus !== 'online') {
          setServerStatus('online');
        }
      }
      
      // Analytics - track successful generation
      if (window.gtag && result && !result.includes('❌')) {
        window.gtag('event', 'pitch_deck_generated', {
          event_category: 'engagement',
          event_label: generateDetailed ? 'detailed' : 'basic',
          value: 1
        });
      }
    } catch (err) {
      console.error("Error generating pitch deck:", err);
      
      // Provide specific error messages based on error type
      if (err.message && err.message.includes('timeout')) {
        setOutput('⏳ Request timed out. The server may be processing your request - please try again in a moment.');
        setServerStatus('busy');
      } else if (err.message && err.message.includes('connect')) {
        setOutput('❌ Cannot connect to server. Please make sure the server is running and try again.');
        setServerStatus('offline');
      } else {
        setOutput('❌ Failed to generate pitch deck. Please try again or check your connection.');
      }
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleSampleClick = (sampleIdea) => {
    setBusinessIdea(sampleIdea);
    setShowLanding(false);
    // Scroll to form
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleClearAll = () => {
    setBusinessIdea('');
    setOutput('');
    setIndustry('');
    setTargetAudience('general investors');
    setFundingStage('seed');
    setGenerateDetailed(false);
    setPresentationStyle('balanced');
    setBusinessModel('');
    setCompetitorContext('');
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(output);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = output;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const downloadAsTxt = () => {
    const element = document.createElement('a');
    const file = new Blob([output], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `pitch-deck-${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleRegenerateWithStyle = async (newStyle) => {
    const originalStyle = presentationStyle;
    setPresentationStyle(newStyle);
    
    setLoading(true);
    setLoadingMessage(`🔄 Regenerating with ${newStyle.replace('-', ' ')} approach...`);
    setOutput('');
    
    try {
      const options = {
        target_audience: targetAudience,
        industry: industry || null,
        funding_stage: fundingStage,
        presentation_style: newStyle,
        business_model: businessModel || null,
        competitor_context: competitorContext || null,
        request_id: `${Date.now()}_${newStyle}_${Math.random().toString(36).substr(2, 9)}`
      };

      console.log("🔄 DEBUG: Regeneration options:", options);

      // Update loading message
      setTimeout(() => {
        if (loading) {
          setLoadingMessage(`✨ Crafting ${newStyle.replace('-', ' ')} pitch deck...`);
        }
      }, 2000);

      const result = generateDetailed 
        ? await generateDetailedPitchDeck(businessIdea, options)
        : await generatePitchDeck(businessIdea, options);
      
      setOutput(result);
    } catch (err) {
      console.error("Error regenerating pitch deck:", err);
      setOutput('❌ Failed to regenerate pitch deck. Please try again.');
      setPresentationStyle(originalStyle); // Restore original style on error
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const downloadAsPDF = async () => {
    if (!isValidOutput) return;
    
    setPdfDownloading(true);
    try {
      // Validate content before generating PDF
      const validation = validateContentForPDF(output);
      
      if (!validation.isValid) {
        const errorMessage = `Cannot generate PDF: ${validation.issues.join(', ')}`;
        console.error('PDF validation failed:', validation);
        alert(errorMessage);
        return;
      }
      
      // Only show warnings for critical issues (score < 30)
      if (validation.score < 30 && validation.issues.length > 0) {
        const criticalIssues = validation.issues.filter(issue => 
          issue.includes('too short') || 
          issue.includes('No slides') || 
          issue.includes('extremely difficult')
        );
        
        if (criticalIssues.length > 0) {
          const warningMessage = `PDF Warning: ${criticalIssues.join(', ')}`;
          console.warn('PDF validation warnings:', validation);
          
          const proceed = window.confirm(
            `${warningMessage}\n\nDo you want to continue with PDF generation?`
          );
          if (!proceed) return;
        }
      }
      
      // Preview structure for debugging
      const structure = previewPDFStructure(output);
      console.log('PDF Structure Preview:', structure);
      
      // Generate filename with more context
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
      const ideaSlug = businessIdea.toLowerCase().replace(/[^a-z0-9]/g, '-').substring(0, 30);
      const filename = `cofoundr-${ideaSlug}-${timestamp}.pdf`;
      
      try {
        const success = downloadPDF(output, { filename });
        
        if (success) {
          // Show success message with structure info
          setCopySuccess(true);
          setTimeout(() => setCopySuccess(false), 3000);
          
          // Optional: Show PDF info to user
          if (structure.totalSlides > 0) {
            console.log(`PDF generated successfully: ${structure.totalSlides} slides, ~${structure.estimatedPages} pages`);
          }
        } else {
          throw new Error('PDF generation returned false');
        }
      } catch (pdfError) {
        throw new Error(pdfError.message || 'PDF generation failed');
      }
    } catch (error) {
      console.error('PDF download error:', error);
      console.error('Content length:', output?.length);
      console.error('Content preview:', output?.substring(0, 300));
      
      // More specific error messages
      let errorMessage = 'Failed to download PDF. ';
      
      if (error.message.includes('Invalid pitch content')) {
        errorMessage += 'The pitch content appears to be invalid. Please try regenerating the pitch deck.';
      } else if (error.message.includes('too short')) {
        errorMessage += 'The pitch content is too short. Please generate a more detailed pitch deck.';
      } else if (error.message.includes('jsPDF')) {
        errorMessage += 'PDF library error. Please try again or contact support.';
      } else {
        errorMessage += 'Please try again. If the problem persists, try regenerating the pitch deck.';
      }
      
      alert(errorMessage);
    } finally {
      setPdfDownloading(false);
    }
  };

  const shareViaEmail = () => {
    const subject = encodeURIComponent('My Startup Pitch Deck');
    const body = encodeURIComponent(`Check out my startup pitch deck:\n\n${output}`);
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  const handleGetStarted = () => {
    setShowLanding(false);
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const getServerStatusColor = () => {
    switch (serverStatus) {
      case 'online': return 'text-green-600';
      case 'offline': return 'text-red-600';
      case 'busy': return 'text-yellow-600';
      default: return 'text-yellow-600';
    }
  };

  const getServerStatusIcon = () => {
    switch (serverStatus) {
      case 'online': return <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>;
      case 'offline': return <div className="w-2.5 h-2.5 rounded-full bg-red-500"></div>;
      case 'busy': return <div className="w-2.5 h-2.5 rounded-full bg-yellow-500"></div>;
      default: return <div className="w-2.5 h-2.5 rounded-full bg-gray-400"></div>;
    }
  };

  const getServerStatusText = () => {
    switch (serverStatus) {
      case 'online': return 'Server online';
      case 'offline': return 'Server offline';
      case 'busy': return 'Server busy';
      case 'checking': return 'Checking...';
      default: return 'Unknown status';
    }
  };

  const isValidOutput = output && !loading && 
    !output.includes('Please enter') && 
    !output.includes('Failed') && 
    !output.includes('❌') &&
    !output.includes('Analyzing your startup');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Cofoundr AI</h1>
                <p className="text-sm text-gray-600">Complete AI Co-founder: Pitch Decks • Logos • Branding • Marketing Copy • Websites</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <span>{getServerStatusIcon()}</span>
                <span className={getServerStatusColor()}>
                  {getServerStatusText()}
                </span>
                {serverStatus === 'online' && isMockMode && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    Mock Mode
                  </span>
                )}
              </div>
              {!showLanding && (
                <button
                  onClick={() => setShowLanding(true)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  ← Back to Home
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Tab Navigation */}
        {!showLanding && (
          <div className="border-t border-gray-200">
            <div className="max-w-7xl mx-auto px-6">
              <div className="flex space-x-8">
                <button
                  onClick={() => setActiveTab('pitch-deck')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'pitch-deck'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="flex items-center"><svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>Pitch Deck Generator</span>
                </button>
                <button
                  onClick={() => setActiveTab('logo-branding')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'logo-branding'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="flex items-center"><svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" /></svg>Logo & Brand Suite</span>
                </button>
                <button
                  onClick={() => setActiveTab('website-generator')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'website-generator'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="flex items-center"><svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>Website Generator</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {showLanding && (
          <div className="animate-fadeInUp">
            <LandingSection onGetStarted={handleGetStarted} />
            
            {/* Quick Start Section */}
            <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center flex items-center justify-center">
                <svg className="w-8 h-8 mr-3 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                Try These Example Ideas
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sampleIdeas.slice(0, 6).map((sampleIdea, index) => (
                  <button
                    key={index}
                    onClick={() => handleSampleClick(sampleIdea)}
                    className="text-left p-4 text-sm text-gray-700 bg-gradient-to-br from-gray-50 to-blue-50 hover:from-blue-50 hover:to-indigo-50 rounded-lg transition-all duration-200 border border-transparent hover:border-blue-200 hover:shadow-md transform hover:-translate-y-1"
                  >
                    <div className="font-medium text-blue-600 mb-1 flex items-center">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                      Startup Idea
                    </div>
                    {sampleIdea}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {!showLanding && (
          <div className="animate-slideInRight">
            {/* Pitch Deck Tab Content */}
            {activeTab === 'pitch-deck' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* Left Column - Input */}
                <div className="space-y-6" ref={formRef}>
                  <div className="bg-white rounded-xl shadow-lg p-6 card-shadow">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  Describe Your Startup Idea
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Startup Idea *
                    </label>
                    <textarea
                      className="w-full p-4 border border-gray-300 rounded-lg resize-vertical focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 form-input"
                      placeholder="Describe your startup idea in detail... (e.g., A mobile app that connects dog owners with local dog walkers using geolocation and real-time scheduling)"
                      value={businessIdea}
                      onChange={(e) => setBusinessIdea(e.target.value)}
                      rows={5}
                    />
                    <div className="flex justify-between items-center mt-2">
                      <p className="text-xs text-gray-500">
                        Be specific about the problem you're solving and your target market
                      </p>
                      <span className={`text-xs ${businessIdea.length < 10 ? 'text-red-500' : businessIdea.length > 500 ? 'text-yellow-500' : 'text-green-500'}`}>
                        {businessIdea.length}/1000
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Audience
                      </label>
                      <select
                        value={targetAudience}
                        onChange={(e) => setTargetAudience(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                      >
                        <option value="general investors">General Investors</option>
                        <option value="angel investors">Angel Investors</option>
                        <option value="VCs">Venture Capitalists</option>
                        <option value="accelerators">Accelerators</option>
                        <option value="corporate investors">Corporate Investors</option>
                        <option value="banks">Banks/Lenders</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Funding Stage
                      </label>
                      <select
                        value={fundingStage}
                        onChange={(e) => setFundingStage(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                      >
                        <option value="idea">Idea Stage</option>
                        <option value="pre-seed">Pre-Seed</option>
                        <option value="seed">Seed</option>
                        <option value="series-a">Series A</option>
                        <option value="series-b">Series B</option>
                        <option value="later-stage">Later Stage</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Industry (Optional)
                    </label>
                    <input
                      type="text"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      placeholder="e.g., FinTech, HealthTech, EdTech, SaaS, E-commerce"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Presentation Style
                      </label>
                      <select
                        value={presentationStyle}
                        onChange={(e) => setPresentationStyle(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                      >
                        <option value="balanced">Balanced Approach</option>
                        <option value="data-driven">Data-Driven & Analytical</option>
                        <option value="storytelling">Storytelling & Emotional</option>
                        <option value="technology-focused">Technology Innovation</option>
                        <option value="market-opportunity">Market Opportunity Driven</option>
                        <option value="problem-solving">Problem-Solving Focused</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Business Model (Optional)
                      </label>
                      <select
                        value={businessModel}
                        onChange={(e) => setBusinessModel(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                      >
                        <option value="">Auto-suggest</option>
                        <option value="subscription">Subscription/SaaS</option>
                        <option value="marketplace">Marketplace</option>
                        <option value="freemium">Freemium</option>
                        <option value="transaction">Transaction Fees</option>
                        <option value="advertising">Advertising Revenue</option>
                        <option value="enterprise">Enterprise Sales</option>
                        <option value="ecommerce">E-commerce</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Known Competitors (Optional)
                    </label>
                    <input
                      type="text"
                      value={competitorContext}
                      onChange={(e) => setCompetitorContext(e.target.value)}
                      placeholder="e.g., Uber, Airbnb, Slack (helps create better positioning)"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 form-input"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Naming competitors helps create more targeted differentiation
                    </p>
                  </div>

                  <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                    <input
                      type="checkbox"
                      id="detailed"
                      checked={generateDetailed}
                      onChange={(e) => setGenerateDetailed(e.target.checked)}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="detailed" className="text-sm text-gray-700">
                      <span className="font-medium">Generate detailed 10-slide deck</span>
                      <br />
                      <span className="text-gray-600">Includes financial projections, competition analysis, and traction metrics</span>
                    </label>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={handleGenerate}
                      disabled={loading || (serverStatus !== 'online' && serverStatus !== 'busy')}
                      className={`flex-1 py-4 px-6 rounded-lg font-semibold text-white transition-all duration-200 btn-hover-scale ${
                        loading || (serverStatus !== 'online' && serverStatus !== 'busy')
                          ? 'bg-gray-400 cursor-not-allowed' 
                          : serverStatus === 'busy'
                          ? 'bg-yellow-500 hover:bg-yellow-600 shadow-lg hover:shadow-xl'
                          : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl'
                      }`}
                    >
                      {loading ? (
                        <div className="flex items-center justify-center space-x-2">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          <span>Generating...</span>
                        </div>
                      ) : serverStatus === 'busy' ? (
                        <span className="flex items-center justify-center"><svg className="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>Generate {generateDetailed ? 'Detailed ' : ''}Pitch Deck (Server Busy)</span>
                      ) : (
                        <span className="flex items-center justify-center"><svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>Generate {generateDetailed ? 'Detailed ' : ''}Pitch Deck</span>
                      )}
                    </button>
                    
                    <button
                      onClick={handleClearAll}
                      className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </div>

              {/* Sample Ideas */}
              <div className="bg-white rounded-xl shadow-lg p-6 card-shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                  Need Inspiration? Try These Ideas:
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                  {sampleIdeas.map((sampleIdea, index) => (
                    <button
                      key={index}
                      onClick={() => handleSampleClick(sampleIdea)}
                      className="w-full text-left p-3 text-sm text-gray-700 bg-gray-50 hover:bg-blue-50 rounded-lg transition-all duration-200 border border-transparent hover:border-blue-200"
                    >
                      {sampleIdea}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - Output */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-lg p-6 card-shadow">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                    <svg className="w-6 h-6 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                    Generated Pitch Deck
                  </h2>
                  {isValidOutput && (
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={copyToClipboard}
                        className={`px-3 py-1 text-sm rounded-md transition-all duration-200 flex items-center ${
                          copySuccess 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        }`}
                      >
                        {copySuccess ? (
                          <>
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                            Copied!
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" /></svg>
                            Copy
                          </>
                        )}
                      </button>
                      
                      {/* PDF Download Button */}
                      <button
                        onClick={downloadAsPDF}
                        disabled={pdfDownloading}
                        className={`px-3 py-1 text-sm rounded-md transition-all duration-200 ${
                          pdfDownloading 
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                            : 'bg-red-100 hover:bg-red-200 text-red-700'
                        }`}
                      >
                        {pdfDownloading ? (
                          <span className="flex items-center space-x-1">
                            <div className="w-3 h-3 border border-red-500 border-t-transparent rounded-full animate-spin"></div>
                            <span>Generating PDF...</span>
                          </span>
                        ) : (
                          <span className="flex items-center"><svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>Download PDF</span>
                        )}
                      </button>
                      
                      <button
                        onClick={downloadAsTxt}
                        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors flex items-center"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                        Download TXT
                      </button>
                      <button
                        onClick={shareViaEmail}
                        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors flex items-center"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                        Share
                      </button>
                      
                      {/* Regenerate with different styles */}
                      <div className="relative group">
                        <button className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                          Try Different Style
                        </button>
                        <div className="absolute right-0 top-8 hidden group-hover:block bg-white shadow-lg rounded-lg border z-10 min-w-48">
                          {[
                            { key: 'data-driven', label: 'Data-Driven', desc: 'Focus on metrics & ROI' },
                            { key: 'storytelling', label: 'Storytelling', desc: 'Emotional & narrative' },
                            { key: 'technology-focused', label: 'Tech-Focused', desc: 'Innovation & IP' },
                            { key: 'market-opportunity', label: 'Market-Driven', desc: 'Timing & disruption' },
                            { key: 'problem-solving', label: 'Problem-Solving', desc: 'Practical solutions' }
                          ].filter(style => style.key !== presentationStyle).map(style => (
                            <button
                              key={style.key}
                              onClick={() => handleRegenerateWithStyle(style.key)}
                              disabled={loading}
                              className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm border-b last:border-b-0 disabled:opacity-50"
                            >
                              <div className="font-medium text-gray-700">{style.label}</div>
                              <div className="text-xs text-gray-500">{style.desc}</div>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="min-h-[500px]">
                  {!output && !loading ? (
                    <div className="flex flex-col items-center justify-center h-96 text-gray-500">
                      <div className="text-blue-500 mb-6">
                        <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" /></svg>
                      </div>
                      <h3 className="text-xl font-medium mb-3 text-gray-700">Ready to Create Your Pitch?</h3>
                      <p className="text-center text-gray-400 max-w-sm">
                        Enter your startup idea on the left and click "Generate Pitch Deck" to get started!
                      </p>
                    </div>
                  ) : loading ? (
                    <LoadingSpinner message={loadingMessage || "Generating your pitch deck..."} />
                  ) : (
                    <div className="prose max-w-none animate-fadeInUp">
                      <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-800 bg-gray-50 p-6 rounded-lg border custom-scrollbar max-h-96 overflow-y-auto">
                        {output}
                      </div>
                      {isValidOutput && (
                        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <span className="text-green-600"><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></span>
                            <span className="text-sm font-medium text-green-800">
                              Pitch deck generated successfully!
                            </span>
                          </div>
                          <p className="text-xs text-green-600 mt-1">
                            You can now copy, download as PDF/TXT, or share your pitch deck using the buttons above.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Tips */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Pro Tips for Better Results
                </h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5"><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg></span>
                    <span>Be specific about your target market and the problem you're solving</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5"><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg></span>
                    <span>Choose a presentation style that matches your audience preferences</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5"><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg></span>
                    <span>Mention competitors to get better positioning and differentiation</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5"><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg></span>
                    <span>Select your business model for more targeted revenue strategies</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5"><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg></span>
                    <span>Try different settings to get varied perspectives on your idea</span>
                  </li>
                </ul>
                
                {serverStatus === 'online' && isMockMode && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-blue-600"><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></span>
                      <span className="text-sm font-medium text-blue-800">Demo Mode Active</span>
                    </div>
                    <p className="text-xs text-blue-700">
                      The server is running in mock mode with sample data. Your generated pitch decks will be realistic examples based on your input, but won't use live AI APIs. This ensures fast responses while you explore the platform!
                    </p>
                  </div>
                )}
              </div>
                </div>
              </div>
              )}
              
              {/* Logo & Branding Tab Content */}
              {activeTab === 'logo-branding' && (
                <div className="w-full">
                  <LogoGenerator 
                    businessIdea={businessIdea}
                    industry={industry}
                    businessModel={businessModel}
                  />
                </div>
              )}
              
              {/* Website Generator Tab Content */}
              {activeTab === 'website-generator' && (
                <div className="w-full">
                  <WebsiteGenerator 
                    businessIdea={businessIdea}
                    industry={industry}
                    businessModel={businessModel}
                    onWebsiteGenerated={(data) => {
                      console.log('Website generated:', data);
                    }}
                  />
                </div>
              )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-6 mb-4">
              <div className="flex items-center space-x-2 text-gray-600">
                <span>🤖</span>
                <span className="text-sm">Powered by AI</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <span>🚀</span>
                <span className="text-sm">Built for Entrepreneurs</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <span>⚡</span>
                <span className="text-sm">Instant Results</span>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              Transform your startup ideas into professional pitch decks in seconds • 
              <span className="text-blue-600 ml-1">Ready to turn your vision into reality?</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
