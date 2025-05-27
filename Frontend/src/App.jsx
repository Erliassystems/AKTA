import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000/api/v1'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchType, setSearchType] = useState('hybrid')
  const [totalResults, setTotalResults] = useState(0)

  const searchProposals = async (query) => {
    if (!query.trim()) {
      setSearchResults([])
      setTotalResults(0)
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        q: query,
        type: searchType,
        limit: 20
      })
      
      const response = await fetch(`${API_BASE}/search?${params}`)
      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      setSearchResults(data.results || [])
      setTotalResults(data.total || 0)
    } catch (err) {
      setError(err.message)
      setSearchResults([])
      setTotalResults(0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    searchProposals(searchQuery)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('de-DE')
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'green'
      case 'rejected': return 'red'
      case 'withdrawn': return 'orange'
      case 'pending': return 'blue'
      default: return 'gray'
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AKTA - Proposal Archive</h1>
        <p>Searchable digital archive for political proposals</p>
      </header>

      <main className="main-content">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-container">
            <input 
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search proposals..."
              className="search-input"
            />
            <button type="submit" disabled={loading} className="search-button">
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div className="search-options">
            <label>
              Search Type:
              <select 
                value={searchType} 
                onChange={(e) => setSearchType(e.target.value)}
                className="search-type-select"
              >
                <option value="hybrid">Hybrid</option>
                <option value="semantic">Semantic</option>
                <option value="fulltext">Full Text</option>
              </select>
            </label>
          </div>
        </form>

        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {totalResults > 0 && (
          <div className="results-info">
            Found {totalResults} proposal{totalResults !== 1 ? 's' : ''}
          </div>
        )}

        <div className="results-container">
          {searchResults.map((proposal) => (
            <div key={proposal.id} className="proposal-card">
              <div className="proposal-header">
                <h3 className="proposal-title">
                  {proposal.proposal_number && (
                    <span className="proposal-number">{proposal.proposal_number}: </span>
                  )}
                  {proposal.title}
                </h3>
                <span 
                  className="status-badge" 
                  style={{ backgroundColor: getStatusColor(proposal.status) }}
                >
                  {proposal.status}
                </span>
              </div>
              
              {proposal.summary && (
                <p className="proposal-summary">{proposal.summary}</p>
              )}
              
              <div className="proposal-meta">
                <span>Date: {formatDate(proposal.submitted_date)}</span>
                {proposal.tags && proposal.tags.length > 0 && (
                  <div className="tags">
                    {proposal.tags.map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
              
              {proposal.relevance_score && (
                <div className="relevance-score">
                  Relevance: {(proposal.relevance_score * 100).toFixed(1)}%
                </div>
              )}
            </div>
          ))}
        </div>

        {searchResults.length === 0 && searchQuery && !loading && !error && (
          <div className="no-results">
            No proposals found for "{searchQuery}"
          </div>
        )}
      </main>
    </div>
  )
}

export default App