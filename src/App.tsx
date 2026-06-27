import Layout from "./components/Layout/Layout";
import Dashboard from "./components/Dashboard/dashboard";
import Chat from "./components/Chat/chat";

function App() {
  return (
    <Layout>
      <Dashboard />
      <Chat />
    </Layout>
  );
}

export default App;