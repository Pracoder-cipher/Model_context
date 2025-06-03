import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { Table } from "@/components/ui/table";
import { Input } from "@/components/ui/input";

const SoftwareApprovalScreen = () => {
  const [swVersion, setSwVersion] = useState("");
  const [requests, setRequests] = useState([]);
  const [comments, setComments] = useState({});
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  useEffect(() => {
    if (swVersion) {
      fetch(`/api/approval-requests?sw_version=${swVersion}`)
        .then((res) => res.json())
        .then((data) => setRequests(data));
    }
  }, [swVersion]);

  const handleDecision = (id, decision) => {
    fetch(`/api/approve/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, comment: comments[id] || "" }),
    }).then(() => {
      setRequests((prev) => prev.filter((req) => req.id !== id));
    });
  };

  const filteredRequests = requests.filter((req) =>
    req.requester.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (filterStatus ? req.status === filterStatus : true)
  );

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Software Approval</h1>
      <Select onValueChange={setSwVersion}>
        <SelectItem value="v1.0">SW Version 1.0</SelectItem>
        <SelectItem value="v2.0">SW Version 2.0</SelectItem>
      </Select>
      
      <div className="flex gap-4 mt-4">
        <Input
          placeholder="Search by requester"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <Select onValueChange={setFilterStatus}>
          <SelectItem value="">All</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="approved">Approved</SelectItem>
          <SelectItem value="rejected">Rejected</SelectItem>
        </Select>
      </div>
      
      <Card className="mt-4">
        <CardContent>
          <Table>
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Requester</th>
                <th>Status</th>
                <th>Comments</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.map((req) => (
                <tr key={req.id}>
                  <td>{req.id}</td>
                  <td>{req.requester}</td>
                  <td>{req.status}</td>
                  <td>
                    <Input
                      placeholder="Add a comment"
                      value={comments[req.id] || ""}
                      onChange={(e) =>
                        setComments({ ...comments, [req.id]: e.target.value })
                      }
                    />
                  </td>
                  <td>
                    <Button onClick={() => handleDecision(req.id, "approved")}>
                      Approve
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => handleDecision(req.id, "rejected")}
                    >
                      Reject
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default SoftwareApprovalScreen;
