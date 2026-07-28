/**
 * MainLayout Component
 *
 * Overall app layout with header, sidebar, and main content area.
 */

import type { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import styles from "./MainLayout.module.css";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className={styles.layout}>
      <Header />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.main} id="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
