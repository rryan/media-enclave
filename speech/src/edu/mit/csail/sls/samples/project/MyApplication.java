package edu.mit.csail.sls.samples.project;

import java.util.LinkedHashMap;
import java.util.Map;

import javax.servlet.http.HttpSession;

import org.w3c.dom.Element;
import org.w3c.dom.Document;

import edu.mit.csail.sls.wami.app.IApplicationController;
import edu.mit.csail.sls.wami.app.IWamiApplication;
import edu.mit.csail.sls.wami.recognition.IRecognitionResult;
import edu.mit.csail.sls.wami.recognition.lightweight.JSGFIncrementalAggregator;
import edu.mit.csail.sls.wami.recognition.lightweight.JSGFIncrementalAggregatorListener;
import edu.mit.csail.sls.wami.util.XmlUtils;

public class MyApplication implements IWamiApplication, JSGFIncrementalAggregatorListener {
	private JSGFIncrementalAggregator aggregator;
	private IApplicationController appController;
	
	@Override
	public void initialize(IApplicationController appController,
			HttpSession session, Map<String, String> paramMap) {
		aggregator = new JSGFIncrementalAggregator(this);
		this.appController = appController;
	}
	 
	 /** 
	 * Called when the "client" (i.e. the GUI in the 
	 * web browser) sends a message to the server.
	 * (i.e. click)
	 */
	@Override
	public void onClientMessage(Element xmlRoot) {
		// TODO Auto-generated method stub
		
	}

	/**
	 * Called when the application is closed.
	 */
	@Override
	public void onClosed() {
		// TODO Auto-generated method stub
		
	}

	/**
	 * Called after audio is finished playing
	 */
	@Override
	public void onFinishedPlayingAudio() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onRecognitionResult(IRecognitionResult result) {
		aggregator.update(result);
	}

	/**
	 * Called when speech recognition begins.
	 */
	@Override
	public void onRecognitionStarted() {
		// TODO Auto-generated method stub
		
	}

	/** 
	 * Called when there are new commands to process.
	 */
	
	private String id = "";
	private String pid = "";
	@Override
	public void processIncremental(LinkedHashMap<String, String> kvs,
			boolean isPartial) {
		String command = kvs.get("command");
		//String id = "";
		if (kvs.get("id")!=null) {
			id = kvs.get("id");
		}
		if (kvs.get("pid")!=null) {
			pid = kvs.get("pid");
		}
		System.out.println(pid);
		//System.out.println(id.equals(""));
		if (isPartial) {
			//do nothing for now
		}
		else {
			if ("queue".equals(command)) {
				System.out.println("queueing...");
				if (!id.equals("")) {	
					sendQueueRequest(id);	
				}
				//else sendQueueRequest("1"); // for debug
			}
			if ("dequeue".equals(command)) {
				//System.out.println("dequeue requested");
				sendDequeueRequest();
			}
			if ("dequeueall".equals(command)) {
				System.out.println("dequeue all requested");
				sendDequeueAllRequest();
			}
			if ("pause".equals(command)) {
				sendPauseRequest();
			}
			if ("resume".equals(command)) {
				sendResumeRequest();
			}
			if ("playlist".equals(command)) {
				if (!pid.equals("")) {
					sendPlaylistRequest(pid);
				}
			}
		}
		
		
		
	}
	
	private void sendQueueRequest(String id) {
		//delegate to js thingy
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "queue");
		root.setAttribute("id", id);
		doc.appendChild(root);
		appController.sendMessage(doc);
	}
	
	private void sendPlaylistRequest(String pid) {
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "playlist");
		root.setAttribute("pid", pid);
		doc.appendChild(root);
		appController.sendMessage(doc);
	}

	private void sendDequeueRequest() {
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "dequeue");
		doc.appendChild(root);
		appController.sendMessage(doc);
	}
	
	private void sendDequeueAllRequest() {
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "dequeueall");
		doc.appendChild(root);
		appController.sendMessage(doc);
	}
	
	private void sendPauseRequest() {
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "pause");
		doc.appendChild(root);
		appController.sendMessage(doc);
	}
	
	private void sendResumeRequest() {
		Document doc = XmlUtils.newXMLDocument();
		Element root = doc.createElement("reply");
		root.setAttribute("type", "resume");
		doc.appendChild(root);
		appController.sendMessage(doc);
	}
	
	
//	//use for search
//	//TODO return a list of results that gets spoken.
//	private void search(String qr) {
//		//delegate to js thingy
//		Document doc = XmlUtils.newXMLDocument();
//	    Element root = doc.createElement("reply"); //I think we want to leave that
//	    root.setAttribute("type", "search");
//	    root.setAttribute("query", qr);
//	    doc.appendChild(root);
//	    appController.sendMessage(doc);
//	}

}














