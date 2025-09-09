import Header from "../../components/Header";
import Navbar from "../../components/Navbar";
import PageContainer from "../../components/PageContainer";
import SearchBox from "../../components/SearchBox";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <Navbar />
      <SearchBox />
      <PageContainer>{children}</PageContainer>
    </>
  );
}
