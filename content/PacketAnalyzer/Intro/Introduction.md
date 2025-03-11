---
title: Introduction
weight: 10
categories:
- PacketAnalyzer
tags:
- PacketAnalyzer
- Intro
toc: true
sidebar:
  hide: false
cascade:
  type: docs
slug: packetanalyzer/intro/introduction
url: packetanalyzer/intro/introduction
---
COMIZOA Packet Analyzer는 **EtherCAT 패킷 캡처 및 분석을 위한 전문 도구**입니다. EtherCAT 네트워크에서 발생하는 데이터를 실시간으로 모니터링하고, 패킷을 분석하여 네트워크 성능을 최적화하며, 오류를 신속하게 진단할 수 있도록 설계되었습니다.

EtherCAT은 고속 실시간 제어가 필요한 산업 자동화 환경에서 널리 사용되는 필드버스 기술입니다. 하지만, 네트워크에서 발생하는 패킷을 직접 분석하고 문제를 진단하는 과정은 쉽지 않습니다. COMIZOA Packet Analyzer는 이러한 문제를 해결하기 위해 **패킷 캡처, 프레임 분석, 에러 탐지 기능을 제공하는 강력한 분석 도구**입니다.

![DashView2](/resources/justgo_03.png)

## 주요 기능

- **EtherCAT 패킷 캡처 및 저장**  
  - 실시간으로 네트워크 트래픽을 캡처하고 `.pcap` 형식으로 저장  
  - Wireshark 수준의 데이터 캡처 성능 제공  

- **EtherCAT 프레임 분석**  
  - PDO, SDO, Register 등의 Read/Write 구분  
  - 슬레이브별 패킷 데이터 확인 및 분석  
  - EtherCAT 명령 단위로 Datagram 추적  
  - PDO 엔트리별 트레이스 및 시각적 차트 제공  

- **에러 검출 및 이상 패턴 분석**  
  - 네트워크 장애 감지 및 통신 끊김 감시
  - 에러 패킷 분석 
  - DI 신호에 대한 노이즈 검출
  - DcSync Timing 에러 검출
  - 슬레이브별 통신 에러 카운터 추적
