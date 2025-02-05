/**

     * automation-baremetal
 * BMCSTest.java   for Bare Metal Compute Service Sanity Check 
 * 2016年10月19日
 
 */

package com.oracle.opc.automation.test.testcase.baremetal;

import java.io.IOException;

import org.testng.annotations.Test;

import com.oracle.opc.automation.common.Constants;
import com.oracle.opc.automation.common.log.AutomationLogger;
import com.oracle.opc.automation.entity.CloudService;
import com.oracle.opc.automation.test.BaseTest;
import com.oracle.opc.automation.test.component.factory.AutomationActionFactory;
import com.oracle.opc.automation.test.testcase.baremetal.action.BMCreateTerminateComputeAction;
import com.oracle.opc.automation.test.testcase.baremetal.action.BMCreateTerminateDatabaseAction;
import com.oracle.opc.automation.test.testcase.baremetal.action.BMCreateTerminateNetworkingAction;

/**
 * @author xueniu
 *
 */

public class BMServiceConsoleTestPhaseOne extends BaseTest {

	private CloudService bm;
	String db_shape;
	String compute_shape;
	boolean byol;

	AutomationLogger logger = new AutomationLogger(BMAccounLifecycle2.class);

	public BMServiceConsoleTestPhaseOne() {
		db_shape = Constants.P_FILE.getProperties().getProperty("db_shape");
		compute_shape = Constants.P_FILE.getProperties()
				.getProperty("compute_shape");
		byol = Boolean.parseBoolean(
				Constants.P_FILE.getProperties().getProperty("byol"));
	}

	// Common code
	public void BM_Create_Compute_Instance(String shape)
			throws InterruptedException, IOException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateComputeAction.class)
				.createComputeInstance(shape);

	}

	public void BM_Create_Database_Instance(String shape, boolean byol)
			throws InterruptedException, IOException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateDatabaseAction.class)
				.createDatabaseInstance(shape, byol);
	}

	// Creation test cases
	@Test
	public void BM_Create_VCN_Instance()
			throws InterruptedException, IOException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateNetworkingAction.class)
				.createVCNInstance();
	}

	@Test(dependsOnMethods = { "BM_Create_VCN_Instance" })
	public void BM_Create_Database_Instance()
			throws InterruptedException, IOException {
		this.BM_Create_Database_Instance(db_shape, byol);
	}

	@Test(dependsOnMethods = { "BM_Create_VCN_Instance" })
	public void BM_Create_Compute_Instance()
			throws InterruptedException, IOException {
		this.BM_Create_Compute_Instance(compute_shape);
	}

	// Termination test cases

	@Test(dependsOnMethods = { "BM_Create_Compute_Instance" })
	public void BM_Terminate_Compute_Instance()
			throws InterruptedException, IOException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateComputeAction.class)
				.terminateComputeInstance();

	}

	@Test(dependsOnMethods = { "BM_Create_Database_Instance" })
	public void BM_Terminate_DB_Instance() throws InterruptedException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateDatabaseAction.class)
				.terminateDatabaseInstance();
	}

	@Test(dependsOnMethods = { "BM_Terminate_DB_Instance",
			"BM_Terminate_Compute_Instance" })
	public void BM_Terminate_VCN_Instance()
			throws InterruptedException, IOException {
		AutomationActionFactory.getInstance()
				.getAction(bm, BMCreateTerminateNetworkingAction.class)
				.terminateVCNInstance();
	}

}
