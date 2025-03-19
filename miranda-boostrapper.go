package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

func main() {
	os.Setenv("PYTHONUNBUFFERED", "true")

	var uvArgs []string = strings.Fields(os.Getenv("MIRANDA_BOOTSTRAPPER_UV_ARGS"))
	if len(uvArgs) == 0 {
		uvArgs = []string{"run", "--with-requirements", "requirements.txt", "--cache-dir", ".uvcache", "main.py"}
	}
	mirandaArgs := os.Args[1:]

	fmt.Println("Starting go wrapper")
	fmt.Println("Miranda arguments:", mirandaArgs)
	fmt.Println("UV arguments:", uvArgs)
	fmt.Println("Launching Miranda")

	args := append(uvArgs, mirandaArgs...)

	cmd := exec.Command("uv", args...)
	if errors.Is(cmd.Err, exec.ErrDot) {
		cmd.Err = nil
	}

	stdout, err := cmd.StdoutPipe()
	cmd.Stderr = cmd.Stdout
	if err != nil {
		log.Fatal(err)
	}

	err = cmd.Start()
	if err != nil {
		log.Fatal(err)
	}
	for {
		tmp := make([]byte, 1024)
		_, err := stdout.Read(tmp)
		fmt.Print(string(tmp))
		if err != nil {
			break
		}
	}

	fmt.Println("Miranda subprocess done, exiting")
}
