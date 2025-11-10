import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import Sidebar from './components/common/Sidebar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import CreatePresentation from './pages/CreatePresentation';
import LivePresentation from './pages/LivePresentation';
import Profile from './pages/Profile';
import PresentationEditor from './components/presentation/PresentationEditor';
import PresentationViewer from './components/presentation/PresentationViewer';
import QuestionList from './components/QA/QuestionList';
import Payment from './components/Payment/Payment';
import InvoiceViewer from './components/Payment/InvoiceViewer';

import './styles/tailwind.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Routes>
            {/* Public routes without layout */}
            <Route path="/" element={<Home />} />
            <Route path="/presentation/:id/view" element={<PresentationViewer />} />
            <Route path="/live/:id" element={<LivePresentation />} />
            
            {/* Protected routes with layout */}
            <Route path="/*" element={
              <>
                <Header />
                <div className="flex flex-1">
                  <Sidebar />
                  <main className="flex-1 p-6">
                    <Routes>
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/profile" element={<Profile />} />
                      <Route path="/presentation/create" element={<CreatePresentation />} />
                      <Route path="/presentation/:id/edit" element={<PresentationEditor />} />
                      <Route path="/presentation/:id/questions" element={<QuestionList />} />
                      <Route path="/payment" element={<Payment />} />
                      <Route path="/invoice/:id" element={<InvoiceViewer />} />
                    </Routes>
                  </main>
                </div>
                <Footer />
              </>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;