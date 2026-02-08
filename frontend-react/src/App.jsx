import { useState, useRef } from 'react'
import './App.css'

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const onButtonClick = () => {
    fileInputRef.current.click()
  }

  const handleFile = async (file) => {
    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드해주세요.')
      return
    }

    setLoading(true)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/detect', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Error:', error)
      alert('이미지 분석 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="container">
      <header>
        <h1>AI 사람 인식기</h1>
        <p>사진을 업로드하면 AI가 사람을 찾아드립니다.</p>
      </header>

      <main>
        {!result && !loading && (
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={onButtonClick}
          >
            <div className="icon">📁</div>
            <p>여기에 이미지를 드래그하거나 <span>클릭하여 업로드</span>하세요</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleChange}
              hidden
            />
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>이미지를 분석하고 있습니다...</p>
          </div>
        )}

        {result && (
          <div className="result-area">
            <div className={`status-card ${result.found ? 'success' : 'error'}`}>
              <h2>{result.found ? '사람 감지 성공!' : '사람 감지 실패'}</h2>
              <p>{result.message}</p>
            </div>

            <div className="image-container">
              {result.image ? (
                <img src={result.image} alt="분석 결과" />
              ) : (
                <p className="no-image-text">이미지를 표시할 수 없습니다.</p>
              )}
            </div>

            <button className="primary-btn" onClick={reset}>
              다른 이미지 분석하기
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
