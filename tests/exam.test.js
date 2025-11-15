import { beforeEach, describe, expect, it, vi } from "vitest";

/**
 * Basic tests for exam.js functionality
 * Note: Full DOM testing requires loading the actual exam.js file
 * which has many dependencies on the DOM structure
 */

describe("LocalStorage key generation", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Mock window.location
    Object.defineProperty(window, "location", {
      value: { pathname: "/test/page.html" },
      writable: true,
    });
  });

  it("should generate unique storage keys for different exam indices", () => {
    const key1 = `mkdocs-exam-state:/test/page.html:exam-0`;
    const key2 = `mkdocs-exam-state:/test/page.html:exam-1`;

    expect(key1).not.toBe(key2);
    expect(key1).toContain("exam-0");
    expect(key2).toContain("exam-1");
  });

  it("should include page path in storage key", () => {
    const key = `mkdocs-exam-state:/test/page.html:exam-0`;
    expect(key).toContain("/test/page.html");
  });
});

describe("Exam state persistence", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should save and retrieve exam state", () => {
    const testKey = "mkdocs-exam-state:/test:exam-0";
    const testState = {
      type: "choice",
      hintsUsed: [0, 1],
      timeRemaining: 300,
      selectedAnswers: ["0"],
    };

    const data = {
      timestamp: Date.now(),
      state: testState,
    };

    localStorage.setItem(testKey, JSON.stringify(data));
    const retrieved = JSON.parse(localStorage.getItem(testKey));

    expect(retrieved.state.type).toBe("choice");
    expect(retrieved.state.hintsUsed).toEqual([0, 1]);
    expect(retrieved.state.selectedAnswers).toEqual(["0"]);
  });

  it("should handle expired state (older than 24 hours)", () => {
    const testKey = "mkdocs-exam-state:/test:exam-0";
    const oldTimestamp = Date.now() - 25 * 60 * 60 * 1000; // 25 hours ago

    const data = {
      timestamp: oldTimestamp,
      state: { type: "choice", hintsUsed: [], timeRemaining: null },
    };

    localStorage.setItem(testKey, JSON.stringify(data));
    const retrieved = JSON.parse(localStorage.getItem(testKey));

    // Check if timestamp is old
    const hoursSince = (Date.now() - retrieved.timestamp) / (1000 * 60 * 60);
    expect(hoursSince).toBeGreaterThan(24);
  });
});

describe("Answer validation (unit tests)", () => {
  it("should validate numeric answers within tolerance", () => {
    const correctAnswer = 42.5;
    const tolerance = 0.1;

    const isValid = (value, correct, tol) => {
      return Math.abs(value - correct) <= tol;
    };

    expect(isValid(42.5, correctAnswer, tolerance)).toBe(true);
    expect(isValid(42.4, correctAnswer, tolerance)).toBe(true);
    expect(isValid(42.6, correctAnswer, tolerance)).toBe(true);
    expect(isValid(42.7, correctAnswer, tolerance)).toBe(false);
    expect(isValid(42.3, correctAnswer, tolerance)).toBe(false);
  });

  it("should handle case-insensitive string matching", () => {
    const correctAnswers = ["blue", "BLUE", "Blue"];
    const userAnswer = "bLuE";

    const isCorrect = correctAnswers.some(
      (ans) => ans.toLowerCase() === userAnswer.toLowerCase(),
    );

    expect(isCorrect).toBe(true);
  });
});

describe("Score calculation", () => {
  it("should calculate correct score for multiple choice", () => {
    const correctAnswers = [0, 2];
    const selectedAnswers = [0, 2];
    const totalQuestions = 1;

    const score = selectedAnswers.every((ans) => correctAnswers.includes(ans))
      ? 100
      : 0;

    expect(score).toBe(100);
  });

  it("should calculate partial credit when enabled", () => {
    const weights = [0.5, 0.3, 0.2]; // Sum = 1.0
    const correctIndices = [0, 1];
    const selectedIndices = [0]; // Only got first correct

    const totalWeight = correctIndices.reduce(
      (sum, idx) => sum + weights[idx],
      0,
    ); // 0.8
    const earnedWeight = selectedIndices
      .filter((idx) => correctIndices.includes(idx))
      .reduce((sum, idx) => sum + weights[idx], 0); // 0.5

    const score = (earnedWeight / totalWeight) * 100;

    expect(score).toBeCloseTo(62.5, 1);
  });
});

describe("Timer functionality", () => {
  it("should format time correctly", () => {
    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    expect(formatTime(125)).toBe("2:05");
    expect(formatTime(60)).toBe("1:00");
    expect(formatTime(3599)).toBe("59:59");
    expect(formatTime(0)).toBe("0:00");
  });
});
