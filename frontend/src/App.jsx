import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Leaderboard from './pages/Leaderboard';
import Register from './pages/Register';
import StartMatch from './pages/StartMatch';
import Spectator from './pages/Spectator';
import Practice from './pages/Practice';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/register" element={<Register />} />
          <Route path="/start-match" element={<StartMatch />} />
          <Route path="/match/:id" element={<Spectator />} />
          <Route path="/match/:id/replay" element={<Spectator />} />
          <Route path="/practice" element={<Practice />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
