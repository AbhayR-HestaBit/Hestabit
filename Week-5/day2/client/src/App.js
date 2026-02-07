import logo from './logo.svg';
import './App.css';

function App() {
  fetch("/api/health")
    .then(res => res.json())
    .then(data => console.log(data));

  return (
    <div>
      <h1>Day 2 Docker Compose</h1>
    </div>
  );
}

export default App;
