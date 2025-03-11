package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"
	"os/exec"
	"regexp"
	"strings"
)

func handleRenderRequest(w http.ResponseWriter, r *http.Request) {
	requestBody, err := io.ReadAll(r.Body)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	output, err := renderText(string(requestBody))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, output)
}

func renderText(content string) (string, error) {
	// D2 명령어 실행에 다크 테마 적용
	command := exec.Command("d2", "--theme=200", "-")
	command.Stdin = bytes.NewBuffer([]byte(content))

	// 명령어를 문자열로 변환하여 로그에 기록
	fullCommand := strings.Join(command.Args, " ")
	log.Printf("Executing command: %s", fullCommand)

	// 명령어 실행 및 에러 처리
	output, err := command.CombinedOutput()
	if err != nil {
		log.Printf("Command failed: %s", err)
		return "", err
	}

	// 출력 결과에서 <svg> 태그만 추출
	outputStr := string(output)
	re := regexp.MustCompile(`(?s)<svg.*</svg>`) // 전체 SVG 태그를 찾는 정규 표현식
	svgOnly := re.FindString(outputStr)          // <svg> 태그만 추출

	return svgOnly, nil
}

func main() {
	http.HandleFunc("/render", handleRenderRequest)
	log.Println("서버가 시작되었습니다. http://localhost:8080 에서 요청을 받아들입니다.")
	http.ListenAndServe(":8080", nil)
}
