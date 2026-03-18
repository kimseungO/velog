<h2 id="네임노드-데이터-meta-data">네임노드 데이터 (Meta Data)</h2>
<h3 id="메모리">메모리</h3>
<ul>
<li>파일 시스템 메타 데이터<ul>
<li>디렉토리, 파일명, 블록, 블록-데이터노드 매핑 정보</li>
<li>톰 화이트, “경험상 백만 블록 당 1.000MB 메모리 사용(보수적)”</li>
</ul>
</li>
</ul>
<h3 id="파일">파일</h3>
<ul>
<li>두 개의 파일 (edits+fsimage=현재 시점의 메타데이터)<ul>
<li>edits: 변경 내역 (모든 메타데이터에대한 로그기록)(1시간 동안 변경 내용)</li>
<li>fsimage: <strong>특정 시점의 데이터 스냅샷</strong> (1시간 전 메타데이터)<ul>
<li>디렉토리, 파일명, 블록, 상태 정보</li>
<li><strong>블록-데이터노드 매핑 정보는 포함하지 않음</strong><ul>
<li>이 정보는 네임노드 구동 시점에, 데이터노드로부터 받음</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
<h2 id="네임노드-구동-과정">네임노드 구동 과정</h2>
<h3 id="1-파일로부터-메모리에-데이터-생성">1. 파일로부터 메모리에 데이터 생성</h3>
<ol>
<li>fsimage를 메모리에 로딩</li>
<li>edits를 읽어와 메모리에 변경 내역 반영</li>
</ol>
<h3 id="2-스냅샷-생성">2. 스냅샷 생성</h3>
<ol>
<li>현재의 메모리 상태를 fsimage로 내림</li>
<li>빈 edits 생성</li>
</ol>
<h3 id="3-데이터-노드로부터-블록-정보-수신">3. 데이터 노드로부터 블록 정보 수신</h3>
<ol>
<li>메모리에 블록-데이터노드 매핑 정보 생성</li>
</ol>
<h3 id="4-정상-서비스-시작">4. 정상 서비스 시작</h3>
<h3 id="안전모드-13-과정-네임노드-서비스-안-됨">안전모드: 1~3 과정, 네임노드 서비스 안 됨</h3>
<h2 id="보조-네임노드">보조 네임노드</h2>
<h3 id="edits는-최초-재시작-할-때만-빔empty">edits는 최초 재시작 할 때만 빔(empty)</h3>
<ul>
<li>운영 중 상태에서 edits가 무한정 커지게 됨</li>
</ul>
<h3 id="보조-네임노드-→-edits-크기-정리">보조 네임노드 → edits 크기 정리</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/11ffa461-f543-43b0-9cdc-027aec765500/image.png" /></p>
<h2 id="hdfs-장애">HDFS 장애</h2>
<ul>
<li><p>블록 깨짐</p>
</li>
<li><p>데이터 노드 장애</p>
</li>
<li><p>네임 노드 장애</p>
</li>
</ul>
<h2 id="블록-깨짐">블록 깨짐</h2>
<h3 id="체크섬-파일-어떤-데이터의-무결성을-확인하기위해-함께-만듦">체크섬 파일 (어떤 데이터의 무결성을 확인하기위해 함께 만듦)</h3>
<ul>
<li>블록과 함께 생성</li>
<li>데이터 노드에 함께 보관</li>
</ul>
<h3 id="데이터-노드">데이터 노드</h3>
<ul>
<li>주기적으로 블록 스캐너 실행(체크섬 오류 확인)</li>
<li>문제 있는 블록을 네임노드에 통지 (하트비트와 함께)</li>
</ul>
<h3 id="클라이언트">클라이언트</h3>
<ul>
<li>블록을 읽을 때 체크섬도 읽어와 오류 확인</li>
<li>오류 있을 시, 네임노드에 해당 블록 오류 통지</li>
</ul>
<h3 id="네임노드">네임노드</h3>
<ul>
<li>통지받은 오류 블록에 해당하는 다른 복제본 복사</li>
<li>오류 블록 소유 데이터 노드에 삭제 지시</li>
</ul>
<h2 id="데이터노드-장애-대응">데이터노드 장애 대응</h2>
<h3 id="데이터-노드-→-네임노드--heart-beat-전송">데이터 노드 → 네임노드 : heart beat 전송</h3>
<ul>
<li>주기적으로 전송</li>
</ul>
<h3 id="네임노드-1">네임노드</h3>
<ul>
<li>데이터노드의 heart beat이 없으면 장애로 판단</li>
<li>장애 데이터노드를 서비스 대상에서 제외</li>
<li>장애 데이터노드가 포함한 블록들에 대한 복제 수행해서 복제본 개수를 맞춤</li>
</ul>
<h2 id="네임노드-장애-대응">네임노드 장애 대응</h2>
<h3 id="하둡10">하둡1.0</h3>
<ul>
<li>SPOF</li>
<li>수동 처리</li>
</ul>
<h3 id="최소">최소</h3>
<ul>
<li>공유파일 시스템(NFS 같은 것)에 edits와 fsimage 보관</li>
<li>노드 장애 발생시, 다른 장비를 네임노드로 사용<ul>
<li>데이터노드로부터 블록 정보 수신 필요</li>
</ul>
</li>
</ul>
<p>*NFS(Network File System)</p>
<h3 id="하둡20-hahigh-ability지원-active-standby-수동-처리">하둡2.0: HA(high ability)지원 (Active-Standby), 수동 처리</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/6243af7e-e821-4b9f-8e60-a8e89a75788c/image.png" /></p>
<h3 id="하둡20-hahigh-ability지원-active-standby-자동-처리">하둡2.0: HA(high ability)지원 (Active-Standby), 자동 처리</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/551d7cbf-c96e-4952-b8e9-fbee95004b65/image.png" /></p>